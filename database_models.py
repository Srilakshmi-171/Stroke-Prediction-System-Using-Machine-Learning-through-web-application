"""
Database initialization script for NeuroCardioAI
Run this to create a fresh database with correct schema
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from database.models import User, Patient, Prediction, MRIAnalysis, HealthMetric, ModelPerformance
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    """Initialize database with all tables and default data"""
    
    print("="*60)
    print("NeuroCardioAI - Database Initialization")
    print("="*60)
    
    # Create database directory if it doesn't exist
    os.makedirs('database', exist_ok=True)
    
    with app.app_context():
        # Drop all tables
        print("\nDropping existing tables...")
        db.drop_all()
        
        # Create all tables
        print("Creating new tables...")
        db.create_all()
        
        # Create admin user
        print("\nCreating admin user...")
        admin = User(
            username='admin',
            email='admin@neurocardio.com',
            full_name='System Administrator',
            role='admin',
            is_active=True,
            created_at=datetime.utcnow()
        )
        admin.set_password('Admin@123')
        db.session.add(admin)
        
        # Create a test patient user
        print("Creating test patient user...")
        patient_user = User(
            username='arun',
            email='arun@example.com',
            full_name='Arun Kumar',
            age=45,
            gender='Male',
            phone='+91 9876543210',
            address='123 Patient Street, Medical City',
            role='patient',
            is_active=True,
            created_at=datetime.utcnow()
        )
        patient_user.set_password('Patient@123')
        db.session.add(patient_user)
        
        # Commit to get user IDs
        db.session.commit()
        
        # Create patient record for test user
        print("Creating patient record...")
        patient = Patient(
            user_id=patient_user.id,
            medical_record_number=f"MRN{datetime.now().strftime('%Y%m%d')}{patient_user.id:04d}",
            blood_type='O+',
            allergies='None',
            medications='None',
            medical_conditions='None',
            emergency_contact='Priya Kumar',
            emergency_phone='+91 9876543211',
            created_at=datetime.utcnow()
        )
        db.session.add(patient)
        
        # Create sample model performance records
        print("Creating model performance records...")
        models = [
            ('Random Forest', 'brain', 0.923, 0.918, 0.905, 0.911, 0.95),
            ('XGBoost', 'brain', 0.941, 0.937, 0.928, 0.932, 0.96),
            ('Neural Network', 'brain', 0.945, 0.941, 0.932, 0.936, 0.96),
            ('1D CNN', 'brain', 0.912, 0.908, 0.897, 0.902, 0.94),
            ('Ensemble', 'brain', 0.963, 0.959, 0.951, 0.955, 0.98),
            ('Random Forest', 'heart', 0.919, 0.915, 0.902, 0.908, 0.94),
            ('XGBoost', 'heart', 0.938, 0.934, 0.925, 0.929, 0.95),
            ('Neural Network', 'heart', 0.942, 0.938, 0.929, 0.933, 0.95),
            ('1D CNN', 'heart', 0.909, 0.905, 0.894, 0.899, 0.93),
            ('Ensemble', 'heart', 0.959, 0.955, 0.947, 0.951, 0.97)
        ]
        
        for name, mtype, acc, prec, rec, f1, auc in models:
            perf = ModelPerformance(
                model_name=name,
                model_type=mtype,
                accuracy=acc,
                precision=prec,
                recall=rec,
                f1_score=f1,
                auc_roc=auc,
                test_size=1000,
                timestamp=datetime.utcnow()
            )
            db.session.add(perf)
        
        # Commit all changes
        db.session.commit()
        
        print("\n" + "="*60)
        print("DATABASE INITIALIZATION COMPLETE")
        print("="=60)
        print(f"\nDatabase created at: database/database.db")
        print(f"\nAdmin credentials:")
        print(f"  Username: admin")
        print(f"  Email: admin@neurocardio.com")
        print(f"  Password: Admin@123")
        print(f"\nTest patient credentials:")
        print(f"  Username: arun")
        print(f"  Email: arun@example.com")
        print(f"  Password: Patient@123")
        print("\n" + "="*60)

if __name__ == "__main__":
    init_database()