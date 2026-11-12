"""
Database initialization script
Run this to create a fresh database with correct schema
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from extensions import db
from database.models import User, Patient, Prediction, MRIScan, MRIAnalysis, GradCAMResult, HealthMetric, ModelPerformance
from datetime import datetime

def init_database():
    """Initialize database with all tables"""
    
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
            name='System Administrator',
            username='admin',
            email='admin@neurocardio.com',
            full_name='System Administrator',
            role='admin',
            is_active=True,
            created_at=datetime.utcnow()
        )
        admin.set_password('Admin@123')
        db.session.add(admin)
        
        # Create test patient user
        print("Creating test patient user...")
        test_user = User(
            name='Arun Kumar',
            username='arun',
            email='arun@example.com',
            full_name='Arun Kumar',
            age=45,
            gender='Male',
            phone='+91 9876543210',
            address='123 Patient Street, Medical City',
            role='user',
            is_active=True,
            created_at=datetime.utcnow()
        )
        test_user.set_password('Patient@123')
        db.session.add(test_user)
        
        # Commit to get user IDs
        db.session.commit()
        
        # Create patient record
        print("Creating patient record...")
        patient = Patient(
            user_id=test_user.id,
            medical_record_number=f"MRN{datetime.now().strftime('%Y%m%d')}{test_user.id:04d}",
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
            ('Ensemble', 'brain', 0.963, 0.959, 0.951, 0.955, 0.98)
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
        print("="*60)
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