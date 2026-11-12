"""
Database models for NeuroCardioAI
Updated to work with existing codebase
"""

from extensions import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


# =========================
# USER MODEL
# =========================
class User(UserMixin, db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False, default='')  # Added default
    username = db.Column(db.String(80), unique=True, nullable=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    password_hash = db.Column(db.String(200), nullable=True)

    # Additional fields
    full_name = db.Column(db.String(100), nullable=True)
    age = db.Column(db.Integer, nullable=True)
    gender = db.Column(db.String(10), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.String(200), nullable=True)

    # Role: user / admin
    role = db.Column(db.String(20), default="user")

    # Status
    is_active = db.Column(db.Boolean, default=True)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)

    # Relationships
    predictions = db.relationship(
        "Prediction",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )

    mri_scans = db.relationship(
        "MRIScan",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )

    patients = db.relationship('Patient', backref='user', lazy=True)

    def set_password(self, password):
        """Set password using both methods for compatibility"""
        self.password = generate_password_hash(password)
        self.password_hash = self.password

    def check_password(self, password):
        """Check password using both methods for compatibility"""
        if self.password and check_password_hash(self.password, password):
            return True
        if self.password_hash and check_password_hash(self.password_hash, password):
            return True
        return False

    def is_admin(self):
        """Check if user is admin"""
        return self.role == 'admin'

    def get_id(self):
        """Get user ID for Flask-Login"""
        return str(self.id)

# =========================
# PATIENT MODEL (for medical records)
# =========================
class Patient(db.Model):
    """Patient medical records"""
    __tablename__ = 'patients'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    medical_record_number = db.Column(db.String(50), unique=True)
    blood_type = db.Column(db.String(5))
    allergies = db.Column(db.Text)
    medications = db.Column(db.Text)
    medical_conditions = db.Column(db.Text)
    emergency_contact = db.Column(db.String(100))
    emergency_phone = db.Column(db.String(20))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    # Relationships
    health_metrics = db.relationship('HealthMetric', backref='patient', lazy=True)


# =========================
# TABULAR PREDICTION MODEL
# =========================
class Prediction(db.Model):

    __tablename__ = "predictions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=True)

    # Input features (for detailed tracking)
    age = db.Column(db.Float)
    gender = db.Column(db.String(10))
    hypertension = db.Column(db.Boolean)
    heart_disease = db.Column(db.Boolean)
    ever_married = db.Column(db.Boolean)
    work_type = db.Column(db.String(50))
    residence_type = db.Column(db.String(20))
    avg_glucose_level = db.Column(db.Float)
    bmi = db.Column(db.Float)
    smoking_status = db.Column(db.String(30))

    # Patient name for quick reference
    patient_name = db.Column(db.String(150))

    # Prediction results
    prediction_type = db.Column(db.String(20))  # 'brain' or 'heart'
    final_risk_score = db.Column(db.Float)
    risk_score = db.Column(db.Float)  # Alias for final_risk_score
    risk_level = db.Column(db.String(20))  # 'Low', 'Moderate', 'High'

    # Model outputs (JSON string)
    model_outputs = db.Column(db.Text)

    # Individual model predictions
    ml_prediction = db.Column(db.Float)
    ann_prediction = db.Column(db.Float)
    cnn_prediction = db.Column(db.Float)
    ensemble_prediction = db.Column(db.Float)

    # Feature importance (JSON)
    feature_importance = db.Column(db.JSON)

    # Doctor recommendations
    doctor_notes = db.Column(db.Text)
    recommendations = db.Column(db.JSON)

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(200))

    # Relationships
    mri_analysis = db.relationship(
        "MRIAnalysis",
        backref="prediction",
        lazy=True,
        uselist=False
    )


# =========================
# MRI SCAN MODEL
# =========================
class MRIScan(db.Model):

    __tablename__ = "mri_scans"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    prediction_id = db.Column(db.Integer, db.ForeignKey('predictions.id'), nullable=True)

    patient_name = db.Column(db.String(150))
    image_path = db.Column(db.String(300))
    mri_risk_score = db.Column(db.Float)
    confidence_score = db.Column(db.Float)  # Alias for mri_risk_score
    scan_type = db.Column(db.String(20))  # 'brain' or 'heart'
    findings = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    gradcam = db.relationship(
        "GradCAMResult",
        backref="mri",
        uselist=False,
        cascade="all, delete-orphan"
    )


# =========================
# MRI ANALYSIS MODEL (for compatibility)
# =========================
class MRIAnalysis(db.Model):
    """MRI analysis results (compatibility with existing code)"""
    __tablename__ = 'mri_analysis'

    id = db.Column(db.Integer, primary_key=True)
    prediction_id = db.Column(db.Integer, db.ForeignKey('predictions.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    mri_scan_id = db.Column(db.Integer, db.ForeignKey('mri_scans.id'), nullable=True)

    image_path = db.Column(db.String(200))
    heatmap_path = db.Column(db.String(200))
    scan_type = db.Column(db.String(20))

    # Analysis results
    findings = db.Column(db.Text)
    confidence_score = db.Column(db.Float)
    abnormalities_detected = db.Column(db.JSON)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# =========================
# GRAD-CAM MODEL
# =========================
class GradCAMResult(db.Model):

    __tablename__ = "gradcam_results"

    id = db.Column(db.Integer, primary_key=True)
    mri_id = db.Column(db.Integer, db.ForeignKey("mri_scans.id"), nullable=False)
    analysis_id = db.Column(db.Integer, db.ForeignKey('mri_analysis.id'), nullable=True)

    heatmap_path = db.Column(db.String(300))
    explanation_score = db.Column(db.Float)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# =========================
# HEALTH METRIC MODEL
# =========================
class HealthMetric(db.Model):
    """User health metrics tracking"""
    __tablename__ = 'health_metrics'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    metric_type = db.Column(db.String(50))  # 'blood_pressure', 'heart_rate', etc.
    value = db.Column(db.Float)
    unit = db.Column(db.String(20))
    notes = db.Column(db.Text)

    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)


# =========================
# MODEL PERFORMANCE MODEL
# =========================
class ModelPerformance(db.Model):
    """Track ML model performance metrics"""
    __tablename__ = 'model_performance'

    id = db.Column(db.Integer, primary_key=True)
    model_name = db.Column(db.String(50))
    model_type = db.Column(db.String(20))  # 'brain' or 'heart'
    accuracy = db.Column(db.Float)
    precision = db.Column(db.Float)
    recall = db.Column(db.Float)
    f1_score = db.Column(db.Float)
    auc_roc = db.Column(db.Float)

    test_size = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


# =========================
# DATABASE INITIALIZATION
# =========================
def init_db():
    """Initialize database with default data"""
    db.create_all()

    # Create admin user if not exists
    admin = User.query.filter_by(role='admin').first()
    if not admin:
        admin = User(
            name='System Administrator',
            username='admin',
            email='admin@neurocardio.com',
            full_name='System Administrator',
            role='admin',
            is_active=True
        )
        admin.set_password('Admin@123')
        db.session.add(admin)
        db.session.commit()
        print("Admin user created successfully")

    # Create test patient if not exists
    test_patient = User.query.filter_by(email='arun@example.com').first()
    if not test_patient:
        test_patient = User(
            name='Arun Kumar',
            username='arun',
            email='arun@example.com',
            full_name='Arun Kumar',
            age=45,
            gender='Male',
            phone='+91 9876543210',
            address='123 Patient Street, Medical City',
            role='user',
            is_active=True
        )
        test_patient.set_password('Patient@123')
        db.session.add(test_patient)
        db.session.commit()

        # Create patient record
        patient = Patient(
            user_id=test_patient.id,
            medical_record_number=f"MRN{datetime.now().strftime('%Y%m%d')}{test_patient.id:04d}",
            blood_type='O+',
            allergies='None',
            medications='None',
            medical_conditions='None',
            emergency_contact='Priya Kumar',
            emergency_phone='+91 9876543211'
        )
        db.session.add(patient)
        db.session.commit()
        print("Test patient created successfully")