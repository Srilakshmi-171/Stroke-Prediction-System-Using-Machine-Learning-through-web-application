"""
Model explainability for NeuroCardioAI
Simplified version without external dependencies
"""

import numpy as np
import logging
import json

logger = logging.getLogger(__name__)

# Flag to indicate SHAP is not available
SHAP_AVAILABLE = False

def generate_shap_explanation(prediction):
    """
    Generate explanation for a saved prediction
    
    Args:
        prediction: Prediction object
        
    Returns:
        Dictionary with explanation data
    """
    try:
        # Feature names for display
        feature_names = ['Age', 'Gender', 'Hypertension', 'Heart Disease', 'Married',
                        'Work Type', 'Residence', 'Glucose Level', 'BMI', 'Smoking Status']
        
        # Calculate importance based on risk factors and actual values
        importance = {}
        
        # Age importance (non-linear, increases with age)
        age = float(prediction.age) if hasattr(prediction, 'age') else 50
        importance['Age'] = min(0.3, (age - 30) / 200)
        
        # Glucose importance
        glucose = float(prediction.avg_glucose_level) if hasattr(prediction, 'avg_glucose_level') else 100
        importance['Glucose Level'] = min(0.25, (glucose - 70) / 800)
        
        # BMI importance
        bmi = float(prediction.bmi) if hasattr(prediction, 'bmi') else 25
        importance['BMI'] = min(0.2, abs(bmi - 22) / 100)
        
        # Hypertension
        importance['Hypertension'] = 0.15 if getattr(prediction, 'hypertension', False) else 0
        
        # Heart Disease
        importance['Heart Disease'] = 0.15 if getattr(prediction, 'heart_disease', False) else 0
        
        # Smoking
        smoking = getattr(prediction, 'smoking_status', 'never smoked')
        if smoking == 'smokes':
            importance['Smoking Status'] = 0.15
        elif smoking == 'formerly smoked':
            importance['Smoking Status'] = 0.08
        else:
            importance['Smoking Status'] = 0
        
        # Gender (small effect)
        importance['Gender'] = 0.03
        
        # Married status
        importance['Married'] = 0.02 if getattr(prediction, 'ever_married', False) else 0
        
        # Work Type (small effect)
        work_type = getattr(prediction, 'work_type', 'Private')
        work_importance = {
            'Private': 0.02,
            'Self-employed': 0.03,
            'Govt_job': 0.02,
            'children': 0.01,
            'Never_worked': 0.01
        }
        importance['Work Type'] = work_importance.get(work_type, 0.02)
        
        # Residence
        residence = getattr(prediction, 'residence_type', 'Urban')
        importance['Residence'] = 0.02 if residence == 'Rural' else 0.01
        
        # Normalize to sum to 1
        total = sum(importance.values())
        if total > 0:
            for key in importance:
                importance[key] = importance[key] / total
        
        # Get top 5 features
        top_features = sorted(importance.items(), key=lambda x: abs(x[1]), reverse=True)[:5]
        
        # Generate waterfall data (simplified)
        base_value = 0.3  # Base risk
        cumulative = base_value
        
        waterfall_data = []
        for feature, value in top_features:
            cumulative += value * 0.5  # Scale for visualization
            waterfall_data.append({
                'feature': feature,
                'value': float(value),
                'cumulative': float(cumulative)
            })
        
        return {
            'success': True,
            'base_value': base_value,
            'shap_values': importance,
            'top_features': [(f, float(v)) for f, v in top_features],
            'feature_names': feature_names,
            'waterfall_data': waterfall_data,
            'explanation_type': 'simplified'
        }
        
    except Exception as e:
        logger.error(f"Error in generate_shap_explanation: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'explanation_type': 'error'
        }

class SHAPExplainer:
    """Simplified explainer class"""
    
    def __init__(self, model_type='brain'):
        self.model_type = model_type
        self.feature_names = ['Age', 'Gender', 'Hypertension', 'Heart Disease', 'Married',
                             'Work Type', 'Residence', 'Glucose Level', 'BMI', 'Smoking Status']
        logger.info(f"SHAPExplainer initialized for {model_type} (simplified mode)")
    
    def explain_prediction(self, features):
        """
        Generate explanation for prediction
        
        Args:
            features: Preprocessed feature array
            
        Returns:
            Dictionary with explanation data
        """
        try:
            # Ensure features is numpy array
            if not isinstance(features, np.ndarray):
                features = np.array(features)
            
            if len(features.shape) == 1:
                features = features.reshape(1, -1)
            
            # Generate simple importance based on feature values
            importance = {}
            for i, name in enumerate(self.feature_names):
                if i < features.shape[1]:
                    # Use absolute feature value as proxy for importance
                    imp = float(np.abs(features[0, i]) * 0.1)
                    importance[name] = min(imp, 0.3)
                else:
                    importance[name] = 0.01
            
            # Normalize
            total = sum(importance.values())
            if total > 0:
                for key in importance:
                    importance[key] = importance[key] / total
            
            # Get top features
            top_features = sorted(importance.items(), key=lambda x: abs(x[1]), reverse=True)[:5]
            
            return {
                'success': True,
                'base_value': 0.3,
                'shap_values': importance,
                'top_features': [(f, float(v)) for f, v in top_features],
                'feature_names': self.feature_names
            }
            
        except Exception as e:
            logger.error(f"Error in explain_prediction: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

def get_feature_interaction(feature1, feature2, value1, value2):
    """
    Calculate simple feature interaction
    
    Args:
        feature1: First feature name
        feature2: Second feature name
        value1: First feature value
        value2: Second feature value
        
    Returns:
        Interaction score
    """
    # Simple multiplicative interaction
    return abs(value1 * value2) * 0.5

# Export everything
__all__ = [
    'generate_shap_explanation',
    'SHAPExplainer',
    'SHAP_AVAILABLE',
    'get_feature_interaction'
]

# Print confirmation
print("="*60)
print("✓ Explainability module loaded successfully")
print(f"  Mode: Simplified (no external dependencies)")
print(f"  Available: {__all__}")
print("="*60)