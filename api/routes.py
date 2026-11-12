"""
Main routes for NeuroCardioAI
Complete version with all necessary routes and fixed dashboard
Includes MRI scans in dashboard
"""

from flask import Blueprint, render_template, jsonify, redirect, url_for, flash, request, send_file
from flask_login import login_required, current_user
from database.models import db, Prediction, User, Patient, MRIScan, MRIAnalysis
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import io
import csv
import json
import logging
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from io import BytesIO
import os

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

logger = logging.getLogger(__name__)
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    """Home page"""
    return render_template('home.html')

@main_bp.route('/about')
def about():
    """About page"""
    return render_template('about.html')
@main_bp.route('/dashboard')
@login_required
def dashboard():
    try:
        predictions = Prediction.query.filter_by(user_id=current_user.id)\
            .order_by(Prediction.created_at.desc()).limit(10).all()

        mri_scans = MRIScan.query.filter_by(user_id=current_user.id)\
            .order_by(MRIScan.created_at.desc()).limit(10).all()

        mri_analyses = MRIAnalysis.query.filter_by(user_id=current_user.id)\
            .order_by(MRIAnalysis.created_at.desc()).limit(10).all()

        latest_prediction = Prediction.query.filter_by(user_id=current_user.id)\
            .order_by(Prediction.created_at.desc()).first()

        # Safe last_checkup
        if latest_prediction and latest_prediction.created_at:
            last_checkup = latest_prediction.created_at.strftime('%d %b %Y')
        else:
            last_checkup = datetime.now().strftime('%d %b %Y')

        stats = {
            'total_predictions': Prediction.query.filter_by(user_id=current_user.id).count(),
            'brain_predictions': Prediction.query.filter_by(user_id=current_user.id, prediction_type='brain').count(),
            'heart_predictions': Prediction.query.filter_by(user_id=current_user.id, prediction_type='heart').count(),
            'total_mri_scans': MRIScan.query.filter_by(user_id=current_user.id).count(),
            'high_risk_count': Prediction.query.filter_by(user_id=current_user.id, risk_level='High').count(),
            'last_checkup': last_checkup
        }

        dates = []
        brain_risk_trend = []
        heart_risk_trend = []

        all_predictions = Prediction.query.filter_by(user_id=current_user.id)\
            .order_by(Prediction.created_at.asc()).limit(30).all()

        for pred in all_predictions:
            if pred.created_at:
                dates.append(pred.created_at.strftime('%m-%d'))
            else:
                dates.append("N/A")

            if pred.prediction_type == "brain":
                brain_risk_trend.append(pred.risk_score if pred.risk_score is not None else 0)
                heart_risk_trend.append(None)
            else:
                brain_risk_trend.append(None)
                heart_risk_trend.append(pred.risk_score if pred.risk_score is not None else 0)

        if latest_prediction:
            current_risk = latest_prediction.risk_score if latest_prediction.risk_score is not None else 0
            current_risk_level = latest_prediction.risk_level if latest_prediction.risk_level else "Low"
            current_risk_value = round(latest_prediction.risk_score, 1) if latest_prediction.risk_score is not None else 0 
        else:
            current_risk = 0
            current_risk_level = "Low"
            current_risk_value = 0
        recent_activities = []

        for pred in predictions:
            recent_activities.append({
                'title': f'{pred.prediction_type.title()} Stroke Prediction',
                'description': f'Risk Score: {pred.risk_score:.1f}% - {pred.risk_level} Risk',
                'timestamp': pred.created_at.strftime('%d %b %Y, %I:%M %p') if pred.created_at else 'N/A',
                'icon': 'brain' if pred.prediction_type == 'brain' else 'heart',
                'color': 'danger' if pred.risk_level == 'High' else 'warning' if pred.risk_level == 'Moderate' else 'success'
            })
        return render_template(
            'user/dashboard.html',
            predictions=predictions,
            mri_scans=mri_scans,
            mri_analyses=mri_analyses,
            stats=stats,
            trend_dates=json.dumps(dates),
            brain_risk_trend=json.dumps(brain_risk_trend),
            heart_risk_trend=json.dumps(heart_risk_trend),
            recent_activities=recent_activities,
            current_risk=current_risk,
            current_risk_level=current_risk_level,
            current_risk_value=current_risk_value
        )

    except Exception as e:
        logger.error(f"Dashboard error: {str(e)}")
        flash("Error loading dashboard", "danger")
        return redirect(url_for('main.home'))
@main_bp.route('/prediction')
@login_required
def prediction():
    """New prediction page"""
    return render_template('user/prediction.html')

@main_bp.route('/result/<int:id>')
@login_required
def view_result(id):
    """View prediction result"""
    try:
        prediction = Prediction.query.get_or_404(id)
        
        # Check authorization
        if prediction.user_id != current_user.id and not current_user.is_admin():
            flash('Unauthorized access', 'danger')
            return redirect(url_for('main.dashboard'))
        
        # Get associated MRI analysis if exists
        mri_analysis = None
        if prediction.mri_analysis:
            mri_analysis = prediction.mri_analysis
        
        # Prepare feature importance data
        feature_names = ['Age', 'Gender', 'Hypertension', 'Heart Disease', 'Married',
                        'Work Type', 'Residence', 'Glucose', 'BMI', 'Smoking']
        feature_importance = [0.15, 0.05, 0.12, 0.10, 0.03, 0.04, 0.02, 0.18, 0.14, 0.17]
        
        # Risk factors breakdown
        risk_factors_values = [
            min(prediction.age / 100, 0.3),
            0.15 if prediction.hypertension else 0,
            0.15 if prediction.heart_disease else 0,
            (prediction.avg_glucose_level - 70) / 230 * 0.2,
            (prediction.bmi - 18.5) / 31.5 * 0.15,
            0.1 if prediction.smoking_status == 'smokes' else 0
        ]
        risk_factors_labels = ['Age', 'Hypertension', 'Heart Disease', 'Glucose', 'BMI', 'Smoking']
        
        return render_template('user/result.html',
                             prediction=prediction,
                             mri_analysis=mri_analysis,
                             feature_names=json.dumps(feature_names),
                             feature_importance=json.dumps(feature_importance),
                             risk_factors_values=json.dumps(risk_factors_values),
                             risk_factors_labels=json.dumps(risk_factors_labels))
    except Exception as e:
        logger.error(f"View result error: {str(e)}")
        flash('Error loading result', 'danger')
        return redirect(url_for('main.dashboard'))

@main_bp.route('/history')
@login_required
def history():
    """User prediction history"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 10
        
        predictions = Prediction.query.filter_by(user_id=current_user.id)\
            .order_by(Prediction.created_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        return render_template('user/history.html', predictions=predictions)
    except Exception as e:
        logger.error(f"History error: {str(e)}")
        flash('Error loading history', 'danger')
        return redirect(url_for('main.dashboard'))

@main_bp.route('/profile')
@login_required
def profile():
    """User profile page"""
    try:
        # Get patient info if exists
        patient = Patient.query.filter_by(user_id=current_user.id).first()
        
        # Get user stats
        stats = {
            'total_predictions': Prediction.query.filter_by(user_id=current_user.id).count(),
            'brain_predictions': Prediction.query.filter_by(user_id=current_user.id, prediction_type='brain').count(),
            'heart_predictions': Prediction.query.filter_by(user_id=current_user.id, prediction_type='heart').count(),
            'total_mri_scans': MRIScan.query.filter_by(user_id=current_user.id).count()
        }
        
        # Get recent activity
        recent_predictions = Prediction.query.filter_by(user_id=current_user.id)\
            .order_by(Prediction.created_at.desc()).limit(5).all()
        
        recent_activities = []
        for pred in recent_predictions:
            recent_activities.append({
                'title': f'{pred.prediction_type.title()} Stroke Prediction',
                'description': f'Risk Score: {pred.risk_score:.1f}% - {pred.risk_level} Risk',
                'timestamp': pred.created_at,
                'icon': 'brain' if pred.prediction_type == 'brain' else 'heart',
                'color': 'danger' if pred.risk_level == 'High' else 'warning' if pred.risk_level == 'Moderate' else 'success'
            })
        
        return render_template('user/profile.html', 
                             patient=patient,
                             stats=stats,
                             recent_activities=recent_activities)
    except Exception as e:
        logger.error(f"Profile error: {str(e)}")
        flash('Error loading profile', 'danger')
        return redirect(url_for('main.dashboard'))

@main_bp.route('/update-profile', methods=['POST'])
@login_required
def update_profile():
    """Update user profile"""
    try:
        # Update user fields
        current_user.full_name = request.form.get('full_name', current_user.full_name)
        current_user.phone = request.form.get('phone', current_user.phone)
        current_user.address = request.form.get('address', current_user.address)
        current_user.age = request.form.get('age', current_user.age, type=int)
        current_user.gender = request.form.get('gender', current_user.gender)
        
        # Update patient info if exists
        patient = Patient.query.filter_by(user_id=current_user.id).first()
        if patient:
            patient.blood_type = request.form.get('blood_type', patient.blood_type)
            patient.allergies = request.form.get('allergies', patient.allergies)
            patient.medications = request.form.get('medications', patient.medications)
            patient.emergency_contact = request.form.get('emergency_contact', patient.emergency_contact)
            patient.emergency_phone = request.form.get('emergency_phone', patient.emergency_phone)
        else:
            # Create patient record if it doesn't exist
            patient = Patient(
                user_id=current_user.id,
                medical_record_number=f"MRN{datetime.now().strftime('%Y%m%d')}{current_user.id:04d}",
                blood_type=request.form.get('blood_type'),
                allergies=request.form.get('allergies'),
                medications=request.form.get('medications'),
                emergency_contact=request.form.get('emergency_contact'),
                emergency_phone=request.form.get('emergency_phone')
            )
            db.session.add(patient)
        
        db.session.commit()
        flash('Profile updated successfully', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"Update profile error: {str(e)}")
        flash(f'Error updating profile: {str(e)}', 'danger')
    
    return redirect(url_for('main.profile'))

@main_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """Change user password"""
    try:
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not current_user.check_password(current_password):
            flash('Current password is incorrect', 'danger')
            return redirect(url_for('main.profile'))
        
        if new_password != confirm_password:
            flash('New passwords do not match', 'danger')
            return redirect(url_for('main.profile'))
        
        if len(new_password) < 8:
            flash('Password must be at least 8 characters', 'danger')
            return redirect(url_for('main.profile'))
        
        current_user.set_password(new_password)
        db.session.commit()
        flash('Password changed successfully', 'success')
    except Exception as e:
        logger.error(f"Change password error: {str(e)}")
        flash(f'Error changing password: {str(e)}', 'danger')
    
    return redirect(url_for('main.profile'))

@main_bp.route('/delete-account', methods=['POST'])
@login_required
def delete_account():
    try:
        user = User.query.get(current_user.id)

        from flask_login import logout_user
        logout_user()

        # 🔥 DELETE DEPENDENT DATA FIRST
        Patient.query.filter_by(user_id=user.id).delete()
        Prediction.query.filter_by(user_id=user.id).delete()
        MRIScan.query.filter_by(user_id=user.id).delete()
        MRIAnalysis.query.filter_by(user_id=user.id).delete()

        # 🔥 NOW DELETE USER
        db.session.delete(user)
        db.session.commit()

        flash('Your account has been deleted successfully', 'info')
        return redirect(url_for('main.home'))

    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting account: {str(e)}', 'danger')
        return redirect(url_for('main.profile'))

@main_bp.route('/download-report/<int:id>')
@login_required
def download_report(id):
    """Download prediction report as PDF"""
    try:
        prediction = Prediction.query.get_or_404(id)

        # Authorization check
        if prediction.user_id != current_user.id and not current_user.is_admin():
            flash('Unauthorized access', 'danger')
            return redirect(url_for('main.dashboard'))

        buffer = io.BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=letter)

        width, height = letter

        # -----------------------
        # Header
        # -----------------------
        pdf.setFillColor(colors.darkblue)
        pdf.rect(0, height-80, width, 80, fill=1)

        pdf.setFillColor(colors.white)
        pdf.setFont("Helvetica-Bold", 20)
        pdf.drawCentredString(width/2, height-45, "NeuroCardioAI Medical Report")

        pdf.setFillColor(colors.black)

        # -----------------------
        # Report Details
        # -----------------------
        pdf.setFont("Helvetica", 12)

        details = [
        ["Report ID", prediction.id],
        ["Date", prediction.created_at.strftime('%Y-%m-%d %H:%M')],
        ["Patient", current_user.full_name or current_user.username],
        ["Prediction Type", f"{prediction.prediction_type.title()} Stroke"]
        ]

        table = Table(details, colWidths=[150,300])

        table.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(0,-1),colors.lightgrey),
        ("GRID",(0,0),(-1,-1),1,colors.grey),
        ("FONTNAME",(0,0),(0,-1),'Helvetica-Bold')
        ]))

        table.wrapOn(pdf, width, height)
        table.drawOn(pdf, 80, height-200)

        # -----------------------
        # Risk Section
        # -----------------------
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(80, height-240, "Risk Assessment")

        risk_data = [
        ["Risk Score", f"{prediction.risk_score:.1f}%"],
        ["Risk Level", prediction.risk_level]
        ]

        risk_table = Table(risk_data, colWidths=[150,200])
        risk_table.setStyle(TableStyle([
        ("GRID",(0,0),(-1,-1),1,colors.grey),
        ("BACKGROUND",(0,0),(0,-1),colors.lightgrey)
        ]))

        risk_table.wrapOn(pdf,width,height)
        risk_table.drawOn(pdf,80,height-310)

        # -----------------------
        # Model Predictions
        # -----------------------
        ml_val = prediction.ml_prediction * 100 if prediction.ml_prediction else 0
        ann_val = prediction.ann_prediction * 100 if prediction.ann_prediction else 0
        cnn_val = prediction.cnn_prediction * 100 if prediction.cnn_prediction else 0
        ensemble_val = prediction.ensemble_prediction * 100 if prediction.ensemble_prediction else 0

        model_data = [
        ["Model","Prediction"],
        ["Random Forest", f"{ml_val:.1f}%"],
        ["Neural Network", f"{ann_val:.1f}%"],
        ["CNN Model", f"{cnn_val:.1f}%"],
        ["Ensemble Model", f"{ensemble_val:.1f}%"]
        ]

        model_table = Table(model_data, colWidths=[200,150])

        model_table.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),colors.darkblue),
        ("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("GRID",(0,0),(-1,-1),1,colors.grey)
        ]))

        model_table.wrapOn(pdf,width,height)
        model_table.drawOn(pdf,80,height-430)

        # -----------------------
        # Patient Information
        # -----------------------
        patient_data = [
        ["Parameter","Value"],
        ["Age", prediction.age],
        ["Gender", prediction.gender],
        ["Hypertension", "Yes" if prediction.hypertension else "No"],
        ["Heart Disease", "Yes" if prediction.heart_disease else "No"],
        ["Glucose Level", f"{prediction.avg_glucose_level:.1f}"],
        ["BMI", f"{prediction.bmi:.1f}"],
        ["Smoking", prediction.smoking_status]
        ]

        patient_table = Table(patient_data, colWidths=[200,150])

        patient_table.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),colors.darkblue),
        ("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("GRID",(0,0),(-1,-1),1,colors.grey)
        ]))

        patient_table.wrapOn(pdf,width,height)
        patient_table.drawOn(pdf,80,height-650)

        # -----------------------
        # Footer
        # -----------------------
        pdf.setFont("Helvetica-Oblique",9)
        pdf.drawString(80,80,"Note: This AI prediction is for informational purposes only.")
        pdf.drawString(80,65,"Consult a healthcare professional for medical advice.")

        pdf.drawRightString(width-50,40,"Page 1")

        pdf.showPage()
        pdf.save()

        buffer.seek(0)

        return send_file(
            buffer,
            as_attachment=True,
            download_name=f"stroke_report_{prediction.id}.pdf",
            mimetype="application/pdf"
        )

    except Exception as e:
        logger.error(f"Download report error: {str(e)}")
        flash(f'Error downloading report: {str(e)}', 'danger')
        return redirect(url_for('main.history'))
@main_bp.route('/export-history')
@login_required
def export_history():
    """Export prediction history as CSV"""
    try:
        predictions = Prediction.query.filter_by(user_id=current_user.id)\
            .order_by(Prediction.created_at.desc()).all()
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['ID', 'Date', 'Type', 'Risk Score', 'Risk Level', 
                        'ML Model', 'ANN Model', 'CNN Model', 'Ensemble Model'])
        
        # Write data
        for pred in predictions:
            writer.writerow([
                pred.id,
                pred.created_at.strftime('%Y-%m-%d %H:%M'),
                pred.prediction_type,
                f"{pred.risk_score:.1f}%",
                pred.risk_level,
                f"{pred.ml_prediction:.3f}" if pred.ml_prediction else 'N/A',
                f"{pred.ann_prediction:.3f}" if pred.ann_prediction else 'N/A',
                f"{pred.cnn_prediction:.3f}" if pred.cnn_prediction else 'N/A',
                f"{pred.ensemble_prediction:.3f}" if pred.ensemble_prediction else 'N/A'
            ])
        
        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            as_attachment=True,
            download_name=f'prediction_history_{datetime.now().strftime("%Y%m%d")}.csv',
            mimetype='text/csv'
        )
    except Exception as e:
        logger.error(f"Export history error: {str(e)}")
        flash(f'Error exporting history: {str(e)}', 'danger')
        return redirect(url_for('main.history'))

@main_bp.route('/send-report/<int:id>', methods=['POST'])
@login_required
def send_report_email(id):
    """Send prediction report via email"""
    try:
        prediction = Prediction.query.get_or_404(id)
        
        # Check authorization
        if prediction.user_id != current_user.id and not current_user.is_admin():
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Get email from request
        data = request.get_json()
        email = data.get('email', current_user.email)
        include_pdf = data.get('include_pdf', False)
        
        # Generate PDF if requested
        pdf_content = None
        if include_pdf:
            from utils.pdf_generator import generate_pdf_report
            pdf_buffer = generate_pdf_report(prediction)
            pdf_content = pdf_buffer.getvalue()
        
        # Send email
        from utils.email_service import send_prediction_report_email
        success = send_prediction_report_email(
            email, 
            prediction, 
            pdf_content=pdf_content
        )
        
        if success:
            return jsonify({
                'success': True, 
                'message': 'Report sent successfully'
            })
        else:
            return jsonify({'error': 'Failed to send email'}), 500
            
    except Exception as e:
        logger.error(f"Send email error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@main_bp.route('/test-email', methods=['POST'])
@login_required
def test_email():
    """Test email functionality"""
    try:
        from utils.email_service import send_welcome_email
        success = send_welcome_email(current_user)
        
        if success:
            return jsonify({
                'success': True, 
                'message': f'Test email sent to {current_user.email}'
            })
        else:
            return jsonify({'error': 'Failed to send email'}), 500
            
    except Exception as e:
        logger.error(f"Test email error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@main_bp.route('/test-email-direct', methods=['GET'])
@login_required
def test_email_direct():
    """Direct email test without prediction"""
    from utils.email_service import send_welcome_email
    
    try:
        # Try to send welcome email
        result = send_welcome_email(current_user)
        
        if result:
            flash(f'✅ Test email sent to {current_user.email}! Check your inbox.', 'success')
        else:
            flash(f'❌ Failed to send email. Check server logs.', 'danger')
            
    except Exception as e:
        flash(f'❌ Error: {str(e)}', 'danger')
    
    return redirect(url_for('main.dashboard'))
@main_bp.route('/debug-email')
@login_required
def debug_email():
    """Debug email functionality"""
    from utils.email_service_debug import test_simple_email
    
    result = test_simple_email()
    
    if result:
        flash('✅ Debug email sent! Check your inbox.', 'success')
    else:
        flash('❌ Debug email failed. Check console for details.', 'danger')
    
    return redirect(url_for('main.dashboard'))
@main_bp.route('/send-test-email')
@login_required
def send_test_email():
    """Send a test email to the current user"""
    from utils.email_service import send_test_email
    
    try:
        result = send_test_email(current_user.email)
        
        if result:
            flash(f'✅ Test email sent to {current_user.email}!', 'success')
        else:
            flash('❌ Failed to send test email. Check server logs.', 'danger')
            
    except Exception as e:
        flash(f'❌ Error: {str(e)}', 'danger')
    
    return redirect(url_for('main.dashboard'))

@main_bp.route('/settings', methods=['GET','POST'])
@login_required
def settings():

    if request.method == 'POST':

        name = request.form.get('name')
        email = request.form.get('email')

        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        # Update profile
        if name:
            current_user.full_name = name

        if email:
            current_user.email = email

        # Password change
        if current_password and new_password and confirm_password:

            if not current_user.check_password(current_password):
                flash("Current password is incorrect", "danger")
                return redirect(url_for('main.settings'))

            if new_password != confirm_password:
                flash("Passwords do not match", "danger")
                return redirect(url_for('main.settings'))

            if len(new_password) < 6:
                flash("Password must be at least 6 characters", "danger")
                return redirect(url_for('main.settings'))

            current_user.set_password(new_password)
            flash("Password updated successfully!", "success")

        db.session.commit()
        flash("Settings updated successfully!", "success")

        return redirect(url_for('main.settings'))

    return render_template('user/settings.html', user=current_user)
    