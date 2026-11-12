"""
Data preprocessing utilities for NeuroCardioAI
Fixed version - ensures exactly 10 features
"""

import numpy as np
import pandas as pd
import joblib
import os
import logging

logger = logging.getLogger(__name__)

# Load preprocessors if they exist
try:
    if os.path.exists('models/scaler.pkl'):
        scaler = joblib.load('models/scaler.pkl')
        logger.info("Loaded scaler from models/scaler.pkl")
    else:
        from sklearn.preprocessing import StandardScaler
        scaler = StandardScaler()
        logger.warning("Scaler not found, using new instance")
except Exception as e:
    logger.error(f"Error loading scaler: {str(e)}")
    from sklearn.preprocessing import StandardScaler
    scaler = StandardScaler()

def get_feature_names():
    """Get list of feature names in correct order (10 features)"""
    return ['age', 'gender', 'hypertension', 'heart_disease', 'ever_married',
            'work_type', 'residence_type', 'avg_glucose_level', 'bmi', 'smoking_status']

def preprocess_input(data):
    """
    Preprocess input data for model prediction
    
    Args:
        data: Dictionary containing input features
        
    Returns:
        Numpy array of preprocessed features (shape: 1, 10)
    """
    try:
        # Convert to DataFrame if dict
        if isinstance(data, dict):
            df = pd.DataFrame([data])
        else:
            df = data.copy()
        
        feature_cols = get_feature_names()
        processed_features = []
        
        for col in feature_cols:
            if col not in df.columns:
                logger.warning(f"Column {col} not found, using default value")
                # Default values for missing columns
                if col in ['age', 'avg_glucose_level', 'bmi']:
                    processed_features.append(50.0)  # Default age/glucose/bmi
                elif col in ['hypertension', 'heart_disease', 'ever_married']:
                    processed_features.append(0.0)
                elif col == 'gender':
                    processed_features.append(0.0)  # Default male
                elif col == 'work_type':
                    processed_features.append(0.0)  # Default Private
                elif col == 'residence_type':
                    processed_features.append(0.0)  # Default Urban
                elif col == 'smoking_status':
                    processed_features.append(0.0)  # Default never smoked
                continue
            
            value = df[col].iloc[0]
            
            if col in ['age', 'avg_glucose_level', 'bmi']:
                try:
                    processed_features.append(float(value))
                except:
                    logger.warning(f"Could not convert {col}={value} to float, using 0")
                    processed_features.append(0.0)
                    
            elif col in ['hypertension', 'heart_disease', 'ever_married']:
                try:
                    processed_features.append(float(value))
                except:
                    processed_features.append(0.0)
                    
            elif col == 'gender':
                try:
                    val_str = str(value).lower()
                    if val_str in ['male', 'm', '0']:
                        processed_features.append(0.0)
                    elif val_str in ['female', 'f', '1']:
                        processed_features.append(1.0)
                    else:
                        processed_features.append(0.0)
                except:
                    processed_features.append(0.0)
                    
            elif col == 'work_type':
                work_map = {
                    'Private': 0.0, 'Self-employed': 1.0, 'Govt_job': 2.0,
                    'children': 3.0, 'Never_worked': 4.0
                }
                try:
                    val_str = str(value)
                    processed_features.append(work_map.get(val_str, 0.0))
                except:
                    processed_features.append(0.0)
                    
            elif col == 'residence_type':
                residence_map = {'Urban': 0.0, 'Rural': 1.0}
                try:
                    val_str = str(value)
                    processed_features.append(residence_map.get(val_str, 0.0))
                except:
                    processed_features.append(0.0)
                    
            elif col == 'smoking_status':
                smoke_map = {
                    'never smoked': 0.0, 'formerly smoked': 1.0,
                    'smokes': 2.0, 'Unknown': 3.0
                }
                try:
                    val_str = str(value)
                    processed_features.append(smoke_map.get(val_str, 0.0))
                except:
                    processed_features.append(0.0)
        
        # Ensure we have exactly 10 features
        if len(processed_features) != 10:
            logger.warning(f"Expected 10 features, got {len(processed_features)}. Adjusting...")
            if len(processed_features) > 10:
                processed_features = processed_features[:10]
            else:
                # Pad with zeros
                processed_features.extend([0.0] * (10 - len(processed_features)))
        
        # Convert to numpy array and ensure float32
        X = np.array(processed_features, dtype=np.float32).reshape(1, -1)
        
        # Scale features if scaler is fitted
        try:
            if hasattr(scaler, 'mean_'):
                X_scaled = scaler.transform(X)
            else:
                X_scaled = X
        except Exception as e:
            logger.warning(f"Scaling failed: {str(e)}, using unscaled data")
            X_scaled = X
        
        logger.debug(f"Preprocessed features shape: {X_scaled.shape}")
        return X_scaled
        
    except Exception as e:
        logger.error(f"Error in preprocess_input: {str(e)}")
        # Return zeros as fallback
        return np.zeros((1, 10), dtype=np.float32)

__all__ = ['preprocess_input', 'get_feature_names', 'scaler']

print("✓ Preprocess module loaded successfully")
print("  - Feature count: 10")