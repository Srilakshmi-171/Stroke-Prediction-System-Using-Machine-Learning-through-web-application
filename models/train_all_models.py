"""
Comprehensive model training script for NeuroCardioAI
Trains all models for brain and heart stroke prediction
"""

import os
import numpy as np
import pandas as pd
import joblib
import pickle
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import StandardScaler, LabelEncoder, MinMaxScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.metrics import (accuracy_score, precision_score, recall_score, f1_score,
                           roc_auc_score, confusion_matrix, classification_report)
from sklearn.impute import SimpleImputer
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models, callbacks
import xgboost as xgb
import lightgbm as lgb
import warnings
warnings.filterwarnings('ignore')

# Create models directory if not exists
os.makedirs('models', exist_ok=True)

class StrokePredictorTrainer:
    """Main trainer class for stroke prediction models"""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.encoder = LabelEncoder()
        self.models = {}
        self.results = {}
        
    def generate_synthetic_data(self, n_samples=10000):
        """Generate synthetic medical data for training"""
        np.random.seed(42)
        
        data = {
            'age': np.random.normal(55, 15, n_samples).clip(18, 100),
            'gender': np.random.choice(['Male', 'Female'], n_samples),
            'hypertension': np.random.choice([0, 1], n_samples, p=[0.8, 0.2]),
            'heart_disease': np.random.choice([0, 1], n_samples, p=[0.85, 0.15]),
            'ever_married': np.random.choice([0, 1], n_samples, p=[0.3, 0.7]),
            'work_type': np.random.choice(['Private', 'Self-employed', 'Govt_job', 'Children', 'Never_worked'], n_samples),
            'residence_type': np.random.choice(['Urban', 'Rural'], n_samples),
            'avg_glucose_level': np.random.normal(100, 30, n_samples).clip(50, 300),
            'bmi': np.random.normal(26, 5, n_samples).clip(15, 50),
            'smoking_status': np.random.choice(['never smoked', 'formerly smoked', 'smokes', 'Unknown'], n_samples)
        }
        
        df = pd.DataFrame(data)
        
        # Generate target with realistic correlations
        risk_score = (
            0.3 * (df['age'] - 50) / 50 +
            0.2 * (df['avg_glucose_level'] - 100) / 200 +
            0.15 * df['hypertension'] +
            0.15 * df['heart_disease'] +
            0.1 * (df['bmi'] - 25) / 25 +
            0.1 * (df['smoking_status'] == 'smokes').astype(int)
        )
        
        # Add noise
        risk_score += np.random.normal(0, 0.1, n_samples)
        
        # Binary target
        df['stroke'] = (risk_score > np.percentile(risk_score, 85)).astype(int)
        
        return df
    
    def preprocess_data(self, df, fit=False):
        """Preprocess the dataframe"""
        # Handle categorical variables
        categorical_cols = ['gender', 'work_type', 'residence_type', 'smoking_status', 'ever_married']
        
        df_processed = df.copy()
        
        # Encode categorical variables
        for col in categorical_cols:
            if col in df.columns:
                if fit:
                    df_processed[col] = self.encoder.fit_transform(df_processed[col].astype(str))
                else:
                    df_processed[col] = self.encoder.transform(df_processed[col].astype(str))
        
        # Handle missing values
        imputer = SimpleImputer(strategy='median')
        numeric_cols = ['age', 'avg_glucose_level', 'bmi']
        
        if fit:
            df_processed[numeric_cols] = imputer.fit_transform(df_processed[numeric_cols])
        else:
            df_processed[numeric_cols] = imputer.transform(df_processed[numeric_cols])
        
        # Scale numeric features
        feature_cols = ['age', 'gender', 'hypertension', 'heart_disease', 'ever_married',
                       'work_type', 'residence_type', 'avg_glucose_level', 'bmi', 'smoking_status']
        
        if fit:
            df_processed[feature_cols] = self.scaler.fit_transform(df_processed[feature_cols])
            # Save scaler
            joblib.dump(self.scaler, 'models/scaler.pkl')
            joblib.dump(self.encoder, 'models/encoder.pkl')
        else:
            df_processed[feature_cols] = self.scaler.transform(df_processed[feature_cols])
        
        return df_processed, feature_cols
    
    def train_tabular_models(self, X_train, X_test, y_train, y_test):
        """Train traditional ML models"""
        print("\n" + "="*60)
        print("Training Tabular Machine Learning Models")
        print("="*60)
        
        models_to_train = {
            'Random Forest': RandomForestClassifier(n_estimators=200, max_depth=15, random_state=42),
            'Gradient Boosting': GradientBoostingClassifier(n_estimators=150, learning_rate=0.1, random_state=42),
            'XGBoost': xgb.XGBClassifier(n_estimators=150, learning_rate=0.1, random_state=42),
            'LightGBM': lgb.LGBMClassifier(n_estimators=150, learning_rate=0.1, random_state=42),
            'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42),
            'SVM': SVC(probability=True, random_state=42)
        }
        
        results = {}
        
        for name, model in models_to_train.items():
            print(f"\nTraining {name}...")
            
            # Train model
            model.fit(X_train, y_train)
            
            # Predictions
            y_pred = model.predict(X_test)
            y_pred_proba = model.predict_proba(X_test)[:, 1]
            
            # Metrics
            accuracy = accuracy_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred)
            recall = recall_score(y_test, y_pred)
            f1 = f1_score(y_test, y_pred)
            roc_auc = roc_auc_score(y_test, y_pred_proba)
            
            results[name] = {
                'model': model,
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'f1': f1,
                'roc_auc': roc_auc
            }
            
            print(f"  Accuracy: {accuracy:.4f}")
            print(f"  Precision: {precision:.4f}")
            print(f"  Recall: {recall:.4f}")
            print(f"  F1-Score: {f1:.4f}")
            print(f"  ROC-AUC: {roc_auc:.4f}")
            
            # Save model
            model_filename = f"models/{name.lower().replace(' ', '_')}_brain.pkl"
            joblib.dump(model, model_filename)
            print(f"  Saved to: {model_filename}")
        
        # Create ensemble model
        print("\nCreating Ensemble Model...")
        estimators = [(name, results[name]['model']) for name in ['Random Forest', 'Gradient Boosting', 'XGBoost']]
        ensemble = VotingClassifier(estimators=estimators, voting='soft')
        ensemble.fit(X_train, y_train)
        
        y_pred_ensemble = ensemble.predict(X_test)
        y_pred_proba_ensemble = ensemble.predict_proba(X_test)[:, 1]
        
        ensemble_results = {
            'model': ensemble,
            'accuracy': accuracy_score(y_test, y_pred_ensemble),
            'precision': precision_score(y_test, y_pred_ensemble),
            'recall': recall_score(y_test, y_pred_ensemble),
            'f1': f1_score(y_test, y_pred_ensemble),
            'roc_auc': roc_auc_score(y_test, y_pred_proba_ensemble)
        }
        
        results['Ensemble'] = ensemble_results
        
        print(f"\nEnsemble Results:")
        print(f"  Accuracy: {ensemble_results['accuracy']:.4f}")
        print(f"  Precision: {ensemble_results['precision']:.4f}")
        print(f"  Recall: {ensemble_results['recall']:.4f}")
        print(f"  F1-Score: {ensemble_results['f1']:.4f}")
        print(f"  ROC-AUC: {ensemble_results['roc_auc']:.4f}")
        
        # Save ensemble
        joblib.dump(ensemble, 'models/ensemble_model.pkl')
        print(f"\nEnsemble saved to: models/ensemble_model.pkl")
        
        # Save best model separately
        best_model_name = max(results, key=lambda x: results[x]['roc_auc'])
        joblib.dump(results[best_model_name]['model'], 'models/brain_ml.pkl')
        print(f"Best model ({best_model_name}) saved as: models/brain_ml.pkl")
        
        return results
    
    def train_ann_model(self, X_train, X_test, y_train, y_test, input_dim):
        """Train Artificial Neural Network"""
        print("\n" + "="*60)
        print("Training Artificial Neural Network (ANN)")
        print("="*60)
        
        # Build ANN model
        model = keras.Sequential([
            layers.Dense(256, activation='relu', input_shape=(input_dim,)),
            layers.BatchNormalization(),
            layers.Dropout(0.3),
            
            layers.Dense(128, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.3),
            
            layers.Dense(64, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.2),
            
            layers.Dense(32, activation='relu'),
            layers.Dropout(0.2),
            
            layers.Dense(16, activation='relu'),
            
            layers.Dense(1, activation='sigmoid')
        ])
        
        # Compile model
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='binary_crossentropy',
            metrics=['accuracy', keras.metrics.Precision(), keras.metrics.Recall(), keras.metrics.AUC()]
        )
        
        # Callbacks
        early_stopping = callbacks.EarlyStopping(
            monitor='val_loss',
            patience=15,
            restore_best_weights=True
        )
        
        reduce_lr = callbacks.ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=5,
            min_lr=0.00001
        )
        
        model_checkpoint = callbacks.ModelCheckpoint(
            'models/best_ann_model.h5',
            monitor='val_accuracy',
            save_best_only=True
        )
        
        # Train model
        history = model.fit(
            X_train, y_train,
            validation_split=0.2,
            epochs=100,
            batch_size=32,
            callbacks=[early_stopping, reduce_lr, model_checkpoint],
            verbose=1
        )
        
        # Evaluate model
        y_pred_proba = model.predict(X_test)
        y_pred = (y_pred_proba > 0.5).astype(int)
        
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred)
        recall = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        roc_auc = roc_auc_score(y_test, y_pred_proba)
        
        print(f"\nANN Results:")
        print(f"  Accuracy: {accuracy:.4f}")
        print(f"  Precision: {precision:.4f}")
        print(f"  Recall: {recall:.4f}")
        print(f"  F1-Score: {f1:.4f}")
        print(f"  ROC-AUC: {roc_auc:.4f}")
        
        # Save model
        model.save('models/brain_ann.h5')
        print(f"\nANN model saved to: models/brain_ann.h5")
        
        return model, history
    
    def train_cnn_model(self, X_train, X_test, y_train, y_test):
        """Train 1D CNN for tabular data"""
        print("\n" + "="*60)
        print("Training 1D Convolutional Neural Network")
        print("="*60)
        
        # Reshape data for 1D CNN
        X_train_cnn = X_train.reshape(X_train.shape[0], X_train.shape[1], 1)
        X_test_cnn = X_test.reshape(X_test.shape[0], X_test.shape[1], 1)
        
        # Build CNN model
        model = keras.Sequential([
            layers.Conv1D(filters=64, kernel_size=3, activation='relu', input_shape=(X_train.shape[1], 1)),
            layers.BatchNormalization(),
            layers.MaxPooling1D(pool_size=2),
            layers.Dropout(0.3),
            
            layers.Conv1D(filters=128, kernel_size=3, activation='relu'),
            layers.BatchNormalization(),
            layers.MaxPooling1D(pool_size=2),
            layers.Dropout(0.3),
            
            layers.Conv1D(filters=64, kernel_size=3, activation='relu'),
            layers.BatchNormalization(),
            layers.GlobalAveragePooling1D(),
            
            layers.Dense(128, activation='relu'),
            layers.Dropout(0.3),
            
            layers.Dense(64, activation='relu'),
            layers.Dropout(0.2),
            
            layers.Dense(32, activation='relu'),
            
            layers.Dense(1, activation='sigmoid')
        ])
        
        # Compile model
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='binary_crossentropy',
            metrics=['accuracy', keras.metrics.Precision(), keras.metrics.Recall(), keras.metrics.AUC()]
        )
        
        # Callbacks
        early_stopping = callbacks.EarlyStopping(
            monitor='val_loss',
            patience=15,
            restore_best_weights=True
        )
        
        # Train model
        history = model.fit(
            X_train_cnn, y_train,
            validation_split=0.2,
            epochs=100,
            batch_size=32,
            callbacks=[early_stopping],
            verbose=1
        )
        
        # Evaluate model
        y_pred_proba = model.predict(X_test_cnn)
        y_pred = (y_pred_proba > 0.5).astype(int)
        
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred)
        recall = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        roc_auc = roc_auc_score(y_test, y_pred_proba)
        
        print(f"\n1D CNN Results:")
        print(f"  Accuracy: {accuracy:.4f}")
        print(f"  Precision: {precision:.4f}")
        print(f"  Recall: {recall:.4f}")
        print(f"  F1-Score: {f1:.4f}")
        print(f"  ROC-AUC: {roc_auc:.4f}")
        
        # Save model
        model.save('models/brain_cnn.h5')
        print(f"\nCNN model saved to: models/brain_cnn.h5")
        
        return model, history
    
    def train_all(self):
        """Main training pipeline"""
        print("\n" + "="*60)
        print("NEUROCARDIOAI - COMPREHENSIVE MODEL TRAINING")
        print("="*60)
        
        # Generate data
        print("\n[1/5] Generating synthetic medical data...")
        df = self.generate_synthetic_data(20000)
        print(f"    Generated {len(df)} samples")
        
        # Preprocess data
        print("\n[2/5] Preprocessing data...")
        df_processed, feature_cols = self.preprocess_data(df, fit=True)
        
        # Prepare features and target
        X = df_processed[feature_cols].values
        y = df_processed['stroke'].values
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        print(f"    Training set: {X_train.shape[0]} samples")
        print(f"    Test set: {X_test.shape[0]} samples")
        
        # Train tabular models (for brain)
        print("\n[3/5] Training tabular ML models...")
        ml_results = self.train_tabular_models(X_train, X_test, y_train, y_test)
        
        # Train ANN
        print("\n[4/5] Training ANN model...")
        ann_model, ann_history = self.train_ann_model(X_train, X_test, y_train, y_test, X_train.shape[1])
        
        # Train 1D CNN
        print("\n[5/5] Training 1D CNN model...")
        cnn_model, cnn_history = self.train_cnn_model(X_train, X_test, y_train, y_test)
        
        # Save final models for heart (using same architecture but different name)
        print("\n" + "="*60)
        print("Creating Heart Stroke Prediction Models")
        print("="*60)
        
        # Copy brain models for heart (in production, train separately)
        import shutil
        shutil.copy('models/brain_ml.pkl', 'models/heart_ml.pkl')
        shutil.copy('models/brain_ann.h5', 'models/heart_ann.h5')
        shutil.copy('models/brain_cnn.h5', 'models/heart_cnn.h5')
        
        print("✓ Heart models created")
        
        # Save model performance metrics
        performance_data = {
            'brain': {
                'ml': {k: v for k, v in ml_results.items() if k != 'model'},
                'ann': {
                    'accuracy': accuracy_score(y_test, (ann_model.predict(X_test) > 0.5).astype(int)),
                    'roc_auc': roc_auc_score(y_test, ann_model.predict(X_test))
                },
                'cnn': {
                    'accuracy': accuracy_score(y_test, (cnn_model.predict(X_test.reshape(X_test.shape[0], X_test.shape[1], 1)) > 0.5).astype(int)),
                    'roc_auc': roc_auc_score(y_test, cnn_model.predict(X_test.reshape(X_test.shape[0], X_test.shape[1], 1)))
                }
            }
        }
        
        with open('models/model_performance.json', 'w') as f:
            import json
            json.dump(performance_data, f, indent=2)
        
        print("\n" + "="*60)
        print("TRAINING COMPLETE!")
        print("="*60)
        print("\nModels saved in 'models/' directory:")
        print("  - brain_ml.pkl (Traditional ML models)")
        print("  - brain_ann.h5 (Artificial Neural Network)")
        print("  - brain_cnn.h5 (1D Convolutional Neural Network)")
        print("  - heart_ml.pkl (Heart ML models)")
        print("  - heart_ann.h5 (Heart ANN)")
        print("  - heart_cnn.h5 (Heart CNN)")
        print("  - ensemble_model.pkl (Ensemble model)")
        print("  - scaler.pkl (Feature scaler)")
        print("  - encoder.pkl (Label encoder)")
        print("  - model_performance.json (Performance metrics)")
        
        return performance_data

if __name__ == "__main__":
    trainer = StrokePredictorTrainer()
    results = trainer.train_all()