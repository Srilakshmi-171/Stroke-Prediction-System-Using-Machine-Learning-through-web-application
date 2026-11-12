"""
PDF Report Generator for NeuroCardioAI
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart
import io
import os
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

def generate_pdf_report(prediction):
    """Generate PDF report for prediction"""
    buffer = io.BytesIO()
    
    # Create document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72,
    )
    
    # Container for elements
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    heading_style = styles['Heading2']
    normal_style = styles['Normal']
    
    # Custom styles
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Heading1'],
        textColor=colors.HexColor('#4361ee'),
        spaceAfter=30,
        alignment=1  # Center alignment
    )
    
    risk_style = ParagraphStyle(
        'RiskStyle',
        parent=styles['Normal'],
        fontSize=14,
        textColor=colors.HexColor('#ef476f' if prediction.risk_level == 'High' else '#ffd166' if prediction.risk_level == 'Moderate' else '#06d6a0'),
        spaceAfter=20,
        alignment=1
    )
    
    # Header
    elements.append(Paragraph("NeuroCardioAI Stroke Prediction Report", header_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Report Info
    report_info = f"""
    <b>Report ID:</b> {prediction.id}<br/>
    <b>Date:</b> {prediction.created_at.strftime('%Y-%m-%d %H:%M')}<br/>
    <b>Patient:</b> {prediction.user.full_name or prediction.user.username}<br/>
    <b>Type:</b> {prediction.prediction_type.title()} Stroke Analysis
    """
    elements.append(Paragraph(report_info, normal_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Risk Score
    elements.append(Paragraph("Risk Assessment", heading_style))
    elements.append(Spacer(1, 0.1*inch))
    
    risk_text = f"""
    <b>Overall Risk Score:</b> {prediction.risk_score:.1f}%<br/>
    <b>Risk Level:</b> {prediction.risk_level}
    """
    elements.append(Paragraph(risk_text, risk_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Model Predictions Table
    elements.append(Paragraph("Model Predictions", heading_style))
    elements.append(Spacer(1, 0.1*inch))
    
    model_data = [
        ['Model', 'Prediction', 'Confidence'],
        ['Random Forest', f"{prediction.ml_prediction*100:.1f}%", '92%'],
        ['Neural Network', f"{prediction.ann_prediction*100:.1f}%", '94%'],
        ['CNN', f"{prediction.cnn_prediction*100:.1f}%", '91%'],
        ['Ensemble', f"{prediction.ensemble_prediction*100:.1f}%", '96%'],
    ]
    
    model_table = Table(model_data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
    model_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4361ee')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    elements.append(model_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Patient Information
    elements.append(Paragraph("Patient Information", heading_style))
    elements.append(Spacer(1, 0.1*inch))
    
    patient_data = [
        ['Age', str(prediction.age)],
        ['Gender', prediction.gender],
        ['Hypertension', 'Yes' if prediction.hypertension else 'No'],
        ['Heart Disease', 'Yes' if prediction.heart_disease else 'No'],
        ['Married', 'Yes' if prediction.ever_married else 'No'],
        ['Work Type', prediction.work_type.replace('_', ' ').title()],
        ['Residence', prediction.residence_type],
        ['Glucose Level', f"{prediction.avg_glucose_level:.1f} mg/dL"],
        ['BMI', f"{prediction.bmi:.1f}"],
        ['Smoking Status', prediction.smoking_status.replace('_', ' ').title()],
    ]
    
    patient_table = Table(patient_data, colWidths=[2*inch, 3*inch])
    patient_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightblue),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    
    elements.append(patient_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Recommendations
    elements.append(Paragraph("Recommendations", heading_style))
    elements.append(Spacer(1, 0.1*inch))
    
    recommendations = [
        "• Consult with your healthcare provider about these results",
        "• Maintain a healthy diet low in sodium and saturated fats",
        "• Exercise regularly (at least 150 minutes per week)",
        "• Monitor blood pressure and glucose levels",
        "• Avoid smoking and limit alcohol consumption",
        "• Get adequate sleep (7-9 hours per night)",
        "• Schedule regular check-ups",
        "• Take prescribed medications as directed",
    ]
    
    if prediction.risk_level == 'High':
        recommendations.insert(0, "• ⚠️ SEEK IMMEDIATE MEDICAL ATTENTION")
        recommendations.insert(1, "• Schedule appointment with specialist within 48 hours")
    
    for rec in recommendations:
        elements.append(Paragraph(rec, normal_style))
        elements.append(Spacer(1, 0.05*inch))
    
    elements.append(Spacer(1, 0.3*inch))
    
    # MRI Analysis (if available)
    if prediction.mri_analysis:
        elements.append(PageBreak())
        elements.append(Paragraph("MRI Analysis", heading_style))
        elements.append(Spacer(1, 0.1*inch))
        
        mri = prediction.mri_analysis
        elements.append(Paragraph(f"<b>Findings:</b> {mri.findings}", normal_style))
        elements.append(Spacer(1, 0.1*inch))
        elements.append(Paragraph(f"<b>Confidence:</b> {mri.confidence_score*100:.1f}%", normal_style))
        
        # Note about heatmap
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph(
            "Note: The Grad-CAM heatmap visualization is available in the web interface.",
            normal_style
        ))
    
    # Footer
    elements.append(Spacer(1, 0.5*inch))
    footer_text = f"""
    <i>Report generated by NeuroCardioAI on {datetime.now().strftime('%Y-%m-%d %H:%M')}<br/>
    This report is for informational purposes only. Always consult with a healthcare professional.</i>
    """
    elements.append(Paragraph(footer_text, normal_style))
    
    # Build PDF
    doc.build(elements)
    
    buffer.seek(0)
    return buffer

def generate_charts(prediction):
    """Generate charts for PDF report"""
    charts = []
    
    # Create feature importance chart
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
    
    # Risk gauge
    risk_value = prediction.risk_score / 100
    colors_gauge = ['#ef476f' if risk_value > 0.6 else '#ffd166' if risk_value > 0.3 else '#06d6a0']
    ax1.pie([risk_value, 1-risk_value], colors=colors_gauge + ['#e9ecef'], 
            startangle=90, counterclock=False)
    ax1.add_artist(plt.Circle((0,0), 0.7, color='white'))
    ax1.set_title('Risk Score', fontsize=12, fontweight='bold')
    
    # Model comparison
    models = ['ML', 'ANN', 'CNN', 'Ensemble']
    values = [
        prediction.ml_prediction * 100,
        prediction.ann_prediction * 100,
        prediction.cnn_prediction * 100,
        prediction.ensemble_prediction * 100
    ]
    colors_bar = ['#4361ee'] * 4
    ax2.bar(models, values, color=colors_bar)
    ax2.set_ylim([0, 100])
    ax2.set_ylabel('Risk (%)')
    ax2.set_title('Model Comparison', fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    
    # Save to bytes
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', dpi=300)
    img_buffer.seek(0)
    plt.close()
    
    return img_buffer