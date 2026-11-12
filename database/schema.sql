-- NeuroCardioAI Database Schema

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(200) NOT NULL,
    full_name VARCHAR(100),
    age INTEGER,
    gender VARCHAR(10),
    phone VARCHAR(20),
    address VARCHAR(200),
    role VARCHAR(20) DEFAULT 'patient',
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- Patients table
CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    medical_record_number VARCHAR(50) UNIQUE,
    blood_type VARCHAR(5),
    allergies TEXT,
    medications TEXT,
    medical_conditions TEXT,
    emergency_contact VARCHAR(100),
    emergency_phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Predictions table
CREATE TABLE IF NOT EXISTS predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    patient_id INTEGER,
    age FLOAT,
    gender VARCHAR(10),
    hypertension BOOLEAN,
    heart_disease BOOLEAN,
    ever_married BOOLEAN,
    work_type VARCHAR(50),
    residence_type VARCHAR(20),
    avg_glucose_level FLOAT,
    bmi FLOAT,
    smoking_status VARCHAR(30),
    prediction_type VARCHAR(20),
    risk_score FLOAT,
    risk_level VARCHAR(20),
    ml_prediction FLOAT,
    ann_prediction FLOAT,
    cnn_prediction FLOAT,
    ensemble_prediction FLOAT,
    feature_importance JSON,
    doctor_notes TEXT,
    recommendations JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),
    user_agent VARCHAR(200),
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (patient_id) REFERENCES patients (id)
);

-- MRI Analysis table
CREATE TABLE IF NOT EXISTS mri_analysis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prediction_id INTEGER,
    user_id INTEGER,
    image_path VARCHAR(200),
    heatmap_path VARCHAR(200),
    scan_type VARCHAR(20),
    findings TEXT,
    confidence_score FLOAT,
    abnormalities_detected JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (prediction_id) REFERENCES predictions (id),
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Health Metrics table
CREATE TABLE IF NOT EXISTS health_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER,
    user_id INTEGER,
    metric_type VARCHAR(50),
    value FLOAT,
    unit VARCHAR(20),
    notes TEXT,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients (id),
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Model Performance table
CREATE TABLE IF NOT EXISTS model_performance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_name VARCHAR(50),
    model_type VARCHAR(20),
    accuracy FLOAT,
    precision FLOAT,
    recall FLOAT,
    f1_score FLOAT,
    auc_roc FLOAT,
    test_size INTEGER,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_predictions_user_id ON predictions(user_id);
CREATE INDEX idx_predictions_created_at ON predictions(created_at);
CREATE INDEX idx_patients_user_id ON patients(user_id);
CREATE INDEX idx_mri_analysis_prediction_id ON mri_analysis(prediction_id);

-- Insert default admin user (password: Admin@123)
INSERT OR IGNORE INTO users (username, email, password_hash, full_name, role, is_active) 
VALUES ('admin', 'admin@neurocardio.com', 
        'pbkdf2:sha256:260000$Z7qX5wQ8$9e8c7b6a5d4c3b2a1f0e9d8c7b6a5d4c3b2a1f0e9d8c7b6a5d4c3b2a1f0e9d8c', 
        'System Administrator', 'admin', 1);