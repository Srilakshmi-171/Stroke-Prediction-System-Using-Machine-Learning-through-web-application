"""
Authentication routes for NeuroCardioAI
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from database.models import db, User, Patient
from datetime import datetime
import logging

# Create blueprint
auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember', False)
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user, remember=remember)
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            logger.info(f"User logged in: {user.email}")
            
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            
            if user.is_admin():
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid email or password', 'danger')
    
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        # Get form data
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        full_name = request.form.get('full_name', '')
        name = request.form.get('name', full_name)  # Use name field if provided, else full_name
        age = request.form.get('age', type=int)
        gender = request.form.get('gender')
        phone = request.form.get('phone')
        address = request.form.get('address')
        
        # Validate required fields
        if not username:
            flash('Username is required', 'danger')
            return redirect(url_for('auth.register'))
        
        if not email:
            flash('Email is required', 'danger')
            return redirect(url_for('auth.register'))
        
        if not password:
            flash('Password is required', 'danger')
            return redirect(url_for('auth.register'))
        
        # Validate
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('auth.register'))
        
        if len(password) < 8:
            flash('Password must be at least 8 characters', 'danger')
            return redirect(url_for('auth.register'))
        
        # Check if user exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('auth.register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return redirect(url_for('auth.register'))
        
        # Create user - ensure name field is set
        user = User(
            name=name or full_name or username,  # Use name, full_name, or username as fallback
            username=username,
            email=email,
            full_name=full_name or name or username,
            age=age,
            gender=gender,
            phone=phone,
            address=address,
            role='patient',
            is_active=True
        )
        user.set_password(password)
        
        try:
            db.session.add(user)
            db.session.flush()  # This will assign an ID without committing
            
            # Create patient record
            patient = Patient(
                user_id=user.id,
                medical_record_number=f"MRN{datetime.now().strftime('%Y%m%d')}{user.id:04d}"
            )
            db.session.add(patient)
            db.session.commit()
            
            logger.info(f"New user registered: {user.email}")
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Registration error: {str(e)}")
            flash('An error occurred during registration. Please try again.', 'danger')
            return redirect(url_for('auth.register'))
    
    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """User logout"""
    logger.info(f"User logged out: {current_user.email}")
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('main.home'))

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():

    if request.method == 'POST':
        email = request.form.get('email')
        phone = request.form.get('phone')
        age = request.form.get('age')

        user = User.query.filter_by(email=email, phone=phone, age=age).first()

        if user:
            return redirect(url_for('auth.reset_password', token=user.id))
        else:
            flash('Identity verification failed', 'danger')

    return render_template('auth/forgot_password.html')

@auth_bp.route('/reset-password/<int:token>', methods=['GET', 'POST'])
def reset_password(token):

    user = User.query.get(token)

    if not user:
        flash('Invalid request', 'danger')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        password = request.form.get('password')
        user.set_password(password)
        db.session.commit()

        flash('Password updated successfully', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/reset_password.html')
@auth_bp.route('/api/check-email', methods=['POST'])
def check_email():
    """API endpoint to check if email exists"""
    data = request.get_json()
    email = data.get('email')
    
    user = User.query.filter_by(email=email).first()
    return jsonify({'exists': user is not None})

@auth_bp.route('/api/check-username', methods=['POST'])
def check_username():
    """API endpoint to check if username exists"""
    data = request.get_json()
    username = data.get('username')
    
    user = User.query.filter_by(username=username).first()
    return jsonify({'exists': user is not None})
@auth_bp.route('/terms')
def terms():
    """Terms of Service page"""
    return render_template('auth/terms.html')


@auth_bp.route('/privacy')
def privacy():
    """Privacy Policy page"""
    return render_template('auth/privacy.html')
