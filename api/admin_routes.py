"""
Admin routes for NeuroCardioAI
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from database.models import db, User, Patient, Prediction, ModelPerformance
from functools import wraps
import pandas as pd
import json
from datetime import datetime, timedelta
import logging
from flask import send_file

# Create blueprint
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
logger = logging.getLogger(__name__)

def admin_required(f):
    """Decorator for admin-only routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please login first', 'warning')
            return redirect(url_for('auth.login'))
        if not current_user.is_admin():
            flash('Admin access required', 'danger')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    """Admin dashboard"""
    # Get statistics
    stats = {
        'total_users': User.query.count(),
        'total_patients': Patient.query.count(),
        'total_predictions': Prediction.query.count(),
        'active_today': User.query.filter(User.last_login >= datetime.utcnow() - timedelta(days=1)).count()
    }
    
    # Get recent predictions
    recent_predictions = Prediction.query.order_by(Prediction.created_at.desc()).limit(10).all()
    
    # Get model performance
    model_perf = ModelPerformance.query.order_by(ModelPerformance.timestamp.desc()).limit(5).all()
    
    # Prepare chart data
    last_7_days = [(datetime.utcnow() - timedelta(days=i)).date() for i in range(6, -1, -1)]
    
    predictions_by_day = []
    for day in last_7_days:
        count = Prediction.query.filter(
            db.func.date(Prediction.created_at) == day
        ).count()
        predictions_by_day.append(count)
    
    return render_template('admin/dashboard.html',
                         stats=stats,
                         recent_predictions=recent_predictions,
                         model_perf=model_perf,
                         chart_labels=[d.strftime('%Y-%m-%d') for d in last_7_days],
                         chart_data=predictions_by_day)

@admin_bp.route('/patients')
@login_required
@admin_required
def patients():
    """Manage patients"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    patients = Patient.query.join(User).order_by(User.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('admin/patients.html', patients=patients)

@admin_bp.route('/patient/<int:id>')
@login_required
@admin_required
def patient_details(id):
    """View patient details"""
    patient = Patient.query.filter_by(user_id=id).first_or_404()
    predictions = Prediction.query.filter_by(user_id=patient.user_id)\
        .order_by(Prediction.created_at.desc()).all()
    
    return render_template('admin/patient_details.html',
                         patient=patient,
                         predictions=predictions)

@admin_bp.route('/analytics')
@login_required
@admin_required
def analytics():
    """View analytics"""
    return render_template('admin/analytics.html')

@admin_bp.route('/model-performance')
@login_required
@admin_required
def model_performance():
    """View model performance"""
    performances = ModelPerformance.query.order_by(ModelPerformance.timestamp.desc()).all()
    return render_template('admin/model_performance.html', performances=performances)

@admin_bp.route('/explainability')
@login_required
@admin_required
def explainability():
    """View model explainability dashboard"""
    return render_template('admin/explainability.html')

@admin_bp.route('/api/stats', methods=['GET'])
@login_required
@admin_required
def get_stats():
    """Get statistics for dashboard"""
    period = request.args.get('period', 'week')
    
    if period == 'day':
        delta = timedelta(days=1)
    elif period == 'week':
        delta = timedelta(weeks=1)
    elif period == 'month':
        delta = timedelta(days=30)
    else:
        delta = timedelta(days=365)
    
    since = datetime.utcnow() - delta
    
    stats = {
        'users': User.query.filter(User.created_at >= since).count(),
        'predictions': Prediction.query.filter(Prediction.created_at >= since).count(),
        'high_risk': Prediction.query.filter(
            Prediction.created_at >= since,
            Prediction.risk_level == 'High'
        ).count(),
        'avg_risk': db.session.query(db.func.avg(Prediction.risk_score))\
            .filter(Prediction.created_at >= since).scalar() or 0
    }
    
    return jsonify(stats)

@admin_bp.route('/api/predictions/timeline', methods=['GET'])
@login_required
@admin_required
def get_prediction_timeline():
    """Get prediction timeline data"""
    days = int(request.args.get('days', 30))
    
    dates = []
    counts = []
    
    for i in range(days, 0, -1):
        date = (datetime.utcnow() - timedelta(days=i)).date()
        count = Prediction.query.filter(
            db.func.date(Prediction.created_at) == date
        ).count()
        
        dates.append(date.strftime('%Y-%m-%d'))
        counts.append(count)
    
    return jsonify({
        'dates': dates,
        'counts': counts
    })

@admin_bp.route('/api/risk-distribution', methods=['GET'])
@login_required
@admin_required
def get_risk_distribution():
    """Get risk level distribution"""
    low = Prediction.query.filter_by(risk_level='Low').count()
    moderate = Prediction.query.filter_by(risk_level='Moderate').count()
    high = Prediction.query.filter_by(risk_level='High').count()
    
    return jsonify({
        'labels': ['Low Risk', 'Moderate Risk', 'High Risk'],
        'values': [low, moderate, high]
    })

@admin_bp.route('/api/model-comparison', methods=['GET'])
@login_required
@admin_required
def get_model_comparison():
    """Get model performance comparison"""
    performances = ModelPerformance.query.order_by(ModelPerformance.timestamp.desc()).limit(10).all()
    
    models = {}
    for perf in performances:
        if perf.model_name not in models:
            models[perf.model_name] = {
                'accuracy': perf.accuracy,
                'precision': perf.precision,
                'recall': perf.recall,
                'f1': perf.f1_score
            }
    
    return jsonify(models)

@admin_bp.route('/user/<int:id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def toggle_user_status(id):
    """Toggle user active status"""
    user = User.query.get_or_404(id)
    user.is_active = not user.is_active
    db.session.commit()
    
    flash(f'User {user.email} {"activated" if user.is_active else "deactivated"}', 'success')
    return redirect(url_for('admin.patients'))

@admin_bp.route('/prediction/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_prediction(id):
    """Delete a prediction"""
    prediction = Prediction.query.get_or_404(id)
    db.session.delete(prediction)
    db.session.commit()
    
    flash('Prediction deleted successfully', 'success')
    return redirect(request.referrer or url_for('admin.dashboard'))


@admin_bp.route('/patients/export', methods=['GET'])
@login_required
@admin_required
def export_patients():
    """Export patients data to CSV"""
    import io
    import csv
    
    patients = Patient.query.all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['User ID', 'Name', 'Email', 'Age', 'Gender', 'Phone', 
                    'Medical Record', 'Blood Type', 'Registered Date', 'Status'])
    
    # Write data
    for patient in patients:
        writer.writerow([
            patient.user_id,
            patient.user.full_name or patient.user.username,
            patient.user.email,
            patient.user.age or 'N/A',
            patient.user.gender or 'N/A',
            patient.user.phone or 'N/A',
            patient.medical_record_number or 'N/A',
            patient.blood_type or 'N/A',
            patient.user.created_at.strftime('%Y-%m-%d'),
            'Active' if patient.user.is_active else 'Inactive'
        ])
    
    output.seek(0)
    
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        as_attachment=True,
        download_name=f'patients_export_{datetime.now().strftime("%Y%m%d")}.csv',
        mimetype='text/csv'
    )
@admin_bp.route('/patient/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_patient(user_id):
    """Edit patient information"""

    patient = Patient.query.filter_by(user_id=user_id).first_or_404()
    user = patient.user

    if request.method == 'POST':
        user.full_name = request.form.get('full_name')
        user.email = request.form.get('email')
        user.age = request.form.get('age')
        user.gender = request.form.get('gender')
        user.phone = request.form.get('phone')

        patient.medical_record_number = request.form.get('medical_record_number')
        patient.blood_type = request.form.get('blood_type')

        db.session.commit()

        flash('Patient updated successfully', 'success')
        return redirect(url_for('admin.patients'))

    return render_template('admin/edit_patient.html', patient=patient)
@admin_bp.route('/system/health', methods=['GET'])
@login_required
@admin_required
def system_health():
    """Get system health metrics"""
    import psutil
    import platform
    
    health_data = {
        'system': platform.system(),
        'python_version': platform.python_version(),
        'cpu_percent': psutil.cpu_percent(interval=1),
        'memory_percent': psutil.virtual_memory().percent,
        'disk_percent': psutil.disk_usage('/').percent,
        'boot_time': datetime.fromtimestamp(psutil.boot_time()).isoformat()
    }
    
    return jsonify(health_data)