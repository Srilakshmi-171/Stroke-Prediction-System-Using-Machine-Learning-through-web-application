"""
MRI Analysis API - Simplified for demonstration
The 3D models are for animation/style only
"""

from flask import Blueprint, request, jsonify, current_app, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from database.models import db, MRIAnalysis, MRIScan
from utils.gradcam import process_mri_scan
import os
from datetime import datetime
import logging

mri_bp = Blueprint('mri', __name__, url_prefix='/mri')
logger = logging.getLogger('mri_analysis')

@mri_bp.route('/analyze', methods=['POST'])
@login_required
def analyze_mri():
    """Analyze MRI scan with visualization"""
    try:
        if 'mri_scan' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['mri_scan']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Get scan type
        scan_type = request.form.get('scan_type', 'brain')
        
        # Save uploaded file
        filename = secure_filename(f"{current_user.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}")
        filepath = os.path.join(current_app.config['MRI_UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Process with visualization
        heatmap_path, findings = process_mri_scan(filepath, scan_type)
        
        # Save to database - First create MRIScan
        mri_scan = MRIScan(
            user_id=current_user.id,
            patient_name=request.form.get('patient_name', 'Unknown'),
            image_path=f"uploads/mri/{filename}",
            scan_type=scan_type,
            findings=findings,
            confidence_score=0.85,
            mri_risk_score=0.85
        )
        db.session.add(mri_scan)
        db.session.flush()  # Get ID without committing
        
        # Create MRI Analysis
        mri_analysis = MRIAnalysis(
            user_id=current_user.id,
            mri_scan_id=mri_scan.id,
            image_path=f"uploads/mri/{filename}",
            heatmap_path=heatmap_path,
            scan_type=scan_type,
            findings=findings,
            confidence_score=0.85
        )
        
        db.session.add(mri_analysis)
        db.session.commit()
        
        logger.info(f"MRI analysis completed for user {current_user.id}, scan ID: {mri_scan.id}")
        
        return jsonify({
            'success': True,
            'analysis_id': mri_analysis.id,
            'scan_id': mri_scan.id,
            'findings': findings,
            'confidence': 0.85,
            'heatmap_url': f"/static/{heatmap_path}",
            'original_url': f"/static/uploads/mri/{filename}"
        })
        
    except Exception as e:
        logger.error(f"MRI analysis error: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@mri_bp.route('/history')
@login_required
def history():
    """View MRI scan history page"""
    try:
        scans = MRIScan.query.filter_by(user_id=current_user.id)\
            .order_by(MRIScan.created_at.desc()).all()
        
        analyses = MRIAnalysis.query.filter_by(user_id=current_user.id)\
            .order_by(MRIAnalysis.created_at.desc()).all()
        
        return render_template('user/mri_history.html', 
                             scans=scans, 
                             analyses=analyses)
    except Exception as e:
        logger.error(f"MRI history error: {str(e)}")
        flash('Error loading MRI history', 'danger')
        return redirect(url_for('main.dashboard'))

@mri_bp.route('/api/history', methods=['GET'])
@login_required
def get_mri_history():
    """Get user's MRI analysis history as JSON"""
    try:
        analyses = MRIAnalysis.query.filter_by(user_id=current_user.id)\
            .order_by(MRIAnalysis.created_at.desc()).all()
        
        scans = MRIScan.query.filter_by(user_id=current_user.id)\
            .order_by(MRIScan.created_at.desc()).all()
        
        return jsonify({
            'success': True,
            'analyses': [{
                'id': a.id,
                'scan_type': a.scan_type,
                'findings': a.findings,
                'confidence': a.confidence_score,
                'created_at': a.created_at.isoformat(),
                'heatmap_url': f"/static/{a.heatmap_path}",
                'image_url': f"/static/{a.image_path}"
            } for a in analyses],
            'scans': [{
                'id': s.id,
                'scan_type': s.scan_type,
                'patient_name': s.patient_name,
                'findings': s.findings,
                'confidence': s.confidence_score,
                'created_at': s.created_at.isoformat(),
                'image_url': f"/static/{s.image_path}"
            } for s in scans]
        })
        
    except Exception as e:
        logger.error(f"MRI history error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@mri_bp.route('/view/<int:scan_id>')
@login_required
def view_mri(scan_id):
    """View MRI scan details and heatmap"""
    try:
        from database.models import MRIScan
        
        scan = MRIScan.query.get_or_404(scan_id)
        
        # Check authorization
        if scan.user_id != current_user.id and not current_user.is_admin():
            flash('Unauthorized access', 'danger')
            return redirect(url_for('main.dashboard'))
        
        # Get associated analysis
        analysis = MRIAnalysis.query.filter_by(mri_scan_id=scan.id).first()
        
        return render_template('user/mri_view.html', 
                             scan=scan, 
                             analysis=analysis)
    except Exception as e:
        logger.error(f"View MRI error: {str(e)}")
        flash('Error loading MRI view', 'danger')
        return redirect(url_for('main.dashboard'))

@mri_bp.route('/analysis/<int:analysis_id>')
@login_required
def view_analysis(analysis_id):
    """View MRI analysis details"""
    try:
        analysis = MRIAnalysis.query.get_or_404(analysis_id)
        
        # Check authorization
        if analysis.user_id != current_user.id and not current_user.is_admin():
            flash('Unauthorized access', 'danger')
            return redirect(url_for('main.dashboard'))
        
        # Get associated scan
        scan = None
        if analysis.mri_scan_id:
            scan = MRIScan.query.get(analysis.mri_scan_id)
        
        return render_template('user/mri_analysis.html', 
                             analysis=analysis,
                             scan=scan)
    except Exception as e:
        logger.error(f"View analysis error: {str(e)}")
        flash('Error loading analysis', 'danger')
        return redirect(url_for('main.dashboard'))

@mri_bp.route('/delete/<int:scan_id>', methods=['POST'])
@login_required
def delete_mri(scan_id):
    """Delete MRI scan and associated analysis"""
    try:
        from database.models import MRIScan, MRIAnalysis
        
        scan = MRIScan.query.get_or_404(scan_id)
        
        # Check authorization
        if scan.user_id != current_user.id and not current_user.is_admin():
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Delete associated analysis first
        analysis = MRIAnalysis.query.filter_by(mri_scan_id=scan.id).first()
        if analysis:
            db.session.delete(analysis)
        
        # Delete the scan
        db.session.delete(scan)
        db.session.commit()
        
        # Try to delete files
        try:
            if scan.image_path:
                file_path = os.path.join(current_app.config['BASE_DIR'], 'static', scan.image_path)
                if os.path.exists(file_path):
                    os.remove(file_path)
            
            if analysis and analysis.heatmap_path:
                heatmap_path = os.path.join(current_app.config['BASE_DIR'], 'static', analysis.heatmap_path)
                if os.path.exists(heatmap_path):
                    os.remove(heatmap_path)
        except Exception as e:
            logger.warning(f"Error deleting files: {str(e)}")
        
        return jsonify({'success': True, 'message': 'MRI scan deleted successfully'})
        
    except Exception as e:
        logger.error(f"Delete MRI error: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@mri_bp.route('/stats')
@login_required
def get_mri_stats():
    """Get MRI statistics for dashboard"""
    try:
        from database.models import MRIScan, MRIAnalysis
        
        total_scans = MRIScan.query.filter_by(user_id=current_user.id).count()
        brain_scans = MRIScan.query.filter_by(user_id=current_user.id, scan_type='brain').count()
        heart_scans = MRIScan.query.filter_by(user_id=current_user.id, scan_type='heart').count()
        
        # Get average confidence
        analyses = MRIAnalysis.query.filter_by(user_id=current_user.id).all()
        avg_confidence = 0
        if analyses:
            avg_confidence = sum(a.confidence_score for a in analyses) / len(analyses)
        
        return jsonify({
            'success': True,
            'stats': {
                'total_scans': total_scans,
                'brain_scans': brain_scans,
                'heart_scans': heart_scans,
                'avg_confidence': avg_confidence
            }
        })
        
    except Exception as e:
        logger.error(f"MRI stats error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@mri_bp.route('/recent')
@login_required
def get_recent_mri():
    """Get recent MRI scans for dashboard widget"""
    try:
        from database.models import MRIScan
        
        recent = MRIScan.query.filter_by(user_id=current_user.id)\
            .order_by(MRIScan.created_at.desc()).limit(5).all()
        
        return jsonify({
            'success': True,
            'recent': [{
                'id': s.id,
                'scan_type': s.scan_type,
                'patient_name': s.patient_name,
                'created_at': s.created_at.isoformat(),
                'confidence': s.confidence_score,
                'image_url': f"/static/{s.image_path}" if s.image_path else None
            } for s in recent]
        })
        
    except Exception as e:
        logger.error(f"Recent MRI error: {str(e)}")
        return jsonify({'error': str(e)}), 500
@mri_bp.route('/upload', methods=['GET'])
@login_required
def upload_mri():
    """MRI upload page"""
    return render_template('user/mri_scans.html')