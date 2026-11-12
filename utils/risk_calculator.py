"""
Risk calculation utilities for stroke prediction
"""

import numpy as np
from datetime import datetime, timedelta

def calculate_framingham_risk(age, gender, systolic_bp, hdl_cholesterol, total_cholesterol, 
                              smoker, diabetic, treated_hypertension):
    """
    Calculate 10-year cardiovascular risk using Framingham Risk Score
    
    Args:
        age: Age in years
        gender: 'Male' or 'Female'
        systolic_bp: Systolic blood pressure in mmHg
        hdl_cholesterol: HDL cholesterol in mg/dL
        total_cholesterol: Total cholesterol in mg/dL
        smoker: Smoking status (boolean)
        diabetic: Diabetes status (boolean)
        treated_hypertension: Hypertension treatment status (boolean)
        
    Returns:
        Risk percentage
    """
    # Coefficients from Framingham study
    if gender.lower() == 'male':
        # Male coefficients
        coef_age = 0.04826
        coef_total_chol = 0.02009
        coef_hdl = -0.01325
        coef_sbp_treated = 0.01341
        coef_sbp_untreated = 0.00887
        coef_smoker = 0.04239
        coef_diabetic = 0.04239
        baseline_survival = 0.88936
        mean_risk = 23.9802
    else:
        # Female coefficients
        coef_age = 0.03334
        coef_total_chol = 0.02009
        coef_hdl = -0.01325
        coef_sbp_treated = 0.01341
        coef_sbp_untreated = 0.00887
        coef_smoker = 0.04239
        coef_diabetic = 0.04239
        baseline_survival = 0.95012
        mean_risk = 26.1931
    
    # Calculate linear predictor
    lp = (coef_age * (age - mean_risk) +
          coef_total_chol * (total_cholesterol - 170) +
          coef_hdl * (hdl_cholesterol - 50))
    
    # Add blood pressure term
    if treated_hypertension:
        lp += coef_sbp_treated * (systolic_bp - 120)
    else:
        lp += coef_sbp_untreated * (systolic_bp - 120)
    
    # Add categorical variables
    if smoker:
        lp += coef_smoker
    if diabetic:
        lp += coef_diabetic
    
    # Calculate risk
    risk = 1 - np.power(baseline_survival, np.exp(lp))
    
    return risk * 100

def calculate_ascvd_risk(age, gender, race, systolic_bp, hdl_cholesterol, total_cholesterol,
                         smoker, diabetic, treated_hypertension):
    """
    Calculate 10-year ASCVD risk using pooled cohort equations
    
    Args:
        age: Age in years (40-79)
        gender: 'Male' or 'Female'
        race: 'White' or 'African American'
        systolic_bp: Systolic blood pressure in mmHg
        hdl_cholesterol: HDL cholesterol in mg/dL
        total_cholesterol: Total cholesterol in mg/dL
        smoker: Smoking status (boolean)
        diabetic: Diabetes status (boolean)
        treated_hypertension: Hypertension treatment status (boolean)
        
    Returns:
        Risk percentage
    """
    # Check age range
    if age < 40 or age > 79:
        return None
    
    # Natural log transformations
    ln_age = np.log(age)
    ln_total_chol = np.log(total_cholesterol)
    ln_hdl = np.log(hdl_cholesterol)
    
    if treated_hypertension:
        ln_sbp = np.log(systolic_bp)
    else:
        ln_sbp = np.log(systolic_bp)
    
    # Coefficients based on race and gender
    if race.lower() == 'white':
        if gender.lower() == 'male':
            # White male coefficients
            coef_ln_age = 12.344
            coef_ln_age_sq = 0
            coef_ln_total_chol = 11.853
            coef_ln_age_ln_total_chol = -2.664
            coef_ln_hdl = -7.990
            coef_ln_age_ln_hdl = 1.769
            coef_ln_sbp_treated = 1.797
            coef_ln_sbp_untreated = 1.764
            coef_smoker = 7.837
            coef_ln_age_smoker = -1.795
            coef_diabetic = 0.658
            mean_risk = 61.18
        else:
            # White female coefficients
            coef_ln_age = -29.799
            coef_ln_age_sq = 4.884
            coef_ln_total_chol = 13.540
            coef_ln_age_ln_total_chol = -3.114
            coef_ln_hdl = -13.578
            coef_ln_age_ln_hdl = 3.149
            coef_ln_sbp_treated = 2.019
            coef_ln_sbp_untreated = 1.957
            coef_smoker = 7.574
            coef_ln_age_smoker = -1.665
            coef_diabetic = 0.661
            mean_risk = -29.18
    else:
        # African American
        if gender.lower() == 'male':
            # African American male coefficients
            coef_ln_age = 2.469
            coef_ln_age_sq = 0
            coef_ln_total_chol = 0.302
            coef_ln_age_ln_total_chol = 0
            coef_ln_hdl = -0.307
            coef_ln_age_ln_hdl = 0
            coef_ln_sbp_treated = 1.916
            coef_ln_sbp_untreated = 1.809
            coef_smoker = 0.549
            coef_ln_age_smoker = 0
            coef_diabetic = 0.645
            mean_risk = 86.61
        else:
            # African American female coefficients
            coef_ln_age = 17.114
            coef_ln_age_sq = 0
            coef_ln_total_chol = 0.940
            coef_ln_age_ln_total_chol = 0
            coef_ln_hdl = -18.920
            coef_ln_age_ln_hdl = 4.475
            coef_ln_sbp_treated = 29.291
            coef_ln_sbp_untreated = 27.820
            coef_smoker = 0.691
            coef_ln_age_smoker = 0
            coef_diabetic = 0.874
            mean_risk = 86.61
    
    # Calculate individual risk score
    ind_sum = (coef_ln_age * ln_age +
               coef_ln_age_sq * ln_age * ln_age +
               coef_ln_total_chol * ln_total_chol +
               coef_ln_age_ln_total_chol * ln_age * ln_total_chol +
               coef_ln_hdl * ln_hdl +
               coef_ln_age_ln_hdl * ln_age * ln_hdl)
    
    # Add blood pressure term
    if treated_hypertension:
        ind_sum += coef_ln_sbp_treated * ln_sbp
    else:
        ind_sum += coef_ln_sbp_untreated * ln_sbp
    
    # Add smoking term
    if smoker:
        ind_sum += coef_smoker + coef_ln_age_smoker * ln_age
    
    # Add diabetes
    if diabetic:
        ind_sum += coef_diabetic
    
    # Calculate risk
    risk = 1 - np.power(0.9144, np.exp(ind_sum - mean_risk))
    
    return risk * 100

def calculate_stroke_risk_simple(age, gender, hypertension, heart_disease, 
                                 avg_glucose, bmi, smoking):
    """
    Simple stroke risk calculation based on key factors
    
    Args:
        age: Age in years
        gender: 'Male' or 'Female'
        hypertension: Boolean
        heart_disease: Boolean
        avg_glucose: Average glucose level
        bmi: Body mass index
        smoking: Smoking status (0: never, 1: former, 2: current)
        
    Returns:
        Risk percentage
    """
    risk = 0
    
    # Age factor (increases with age)
    if age < 40:
        risk += 5
    elif age < 50:
        risk += 10
    elif age < 60:
        risk += 20
    elif age < 70:
        risk += 30
    else:
        risk += 40
    
    # Gender factor (men slightly higher risk)
    if gender.lower() == 'male':
        risk += 5
    
    # Hypertension
    if hypertension:
        risk += 15
    
    # Heart disease
    if heart_disease:
        risk += 20
    
    # Glucose level
    if avg_glucose > 200:
        risk += 15
    elif avg_glucose > 140:
        risk += 10
    elif avg_glucose > 100:
        risk += 5
    
    # BMI
    if bmi > 30:
        risk += 10
    elif bmi > 25:
        risk += 5
    
    # Smoking
    if smoking == 2:  # Current smoker
        risk += 15
    elif smoking == 1:  # Former smoker
        risk += 5
    
    # Cap at 100
    return min(risk, 100)

def calculate_risk_trend(predictions):
    """
    Calculate risk trend from historical predictions
    
    Args:
        predictions: List of Prediction objects
        
    Returns:
        Dictionary with trend analysis
    """
    if len(predictions) < 2:
        return {
            'trend': 'stable',
            'change': 0,
            'direction': 'none'
        }
    
    # Sort by date
    sorted_preds = sorted(predictions, key=lambda x: x.created_at)
    
    # Calculate average change per day
    first_risk = sorted_preds[0].risk_score
    last_risk = sorted_preds[-1].risk_score
    
    time_diff = (sorted_preds[-1].created_at - sorted_preds[0].created_at).days
    if time_diff == 0:
        time_diff = 1
    
    change_per_day = (last_risk - first_risk) / time_diff
    
    # Determine trend
    if change_per_day > 0.5:
        trend = 'increasing'
        direction = 'up'
    elif change_per_day < -0.5:
        trend = 'decreasing'
        direction = 'down'
    else:
        trend = 'stable'
        direction = 'flat'
    
    return {
        'trend': trend,
        'change': abs(last_risk - first_risk),
        'direction': direction,
        'first_risk': first_risk,
        'last_risk': last_risk,
        'change_per_day': change_per_day
    }

def get_risk_color(risk_score):
    """
    Get color code for risk score
    
    Args:
        risk_score: Risk percentage (0-100)
        
    Returns:
        Color hex code
    """
    if risk_score < 30:
        return '#06d6a0'  # Green
    elif risk_score < 60:
        return '#ffd166'  # Yellow
    else:
        return '#ef476f'  # Red

def get_risk_level(risk_score):
    """
    Get risk level category
    
    Args:
        risk_score: Risk percentage (0-100)
        
    Returns:
        Risk level string
    """
    if risk_score < 30:
        return 'Low'
    elif risk_score < 60:
        return 'Moderate'
    else:
        return 'High'

def calculate_lifetime_risk(current_age, risk_factors):
    """
    Calculate lifetime stroke risk
    
    Args:
        current_age: Current age in years
        risk_factors: Dictionary of risk factors
        
    Returns:
        Lifetime risk percentage
    """
    # Base lifetime risk
    base_risk = 25  # 25% baseline
    
    # Adjust for age
    age_factor = max(0, (80 - current_age) / 10)
    
    # Adjust for risk factors
    factor_multiplier = 1.0
    
    if risk_factors.get('hypertension', False):
        factor_multiplier *= 1.5
    
    if risk_factors.get('heart_disease', False):
        factor_multiplier *= 1.8
    
    if risk_factors.get('diabetes', False):
        factor_multiplier *= 1.3
    
    smoking = risk_factors.get('smoking', 0)
    if smoking == 2:  # Current smoker
        factor_multiplier *= 1.6
    elif smoking == 1:  # Former smoker
        factor_multiplier *= 1.2
    
    bmi = risk_factors.get('bmi', 25)
    if bmi > 30:
        factor_multiplier *= 1.4
    elif bmi > 25:
        factor_multiplier *= 1.2
    
    # Calculate lifetime risk
    lifetime_risk = base_risk * factor_multiplier * (age_factor + 0.5)
    
    return min(lifetime_risk, 90)  # Cap at 90%