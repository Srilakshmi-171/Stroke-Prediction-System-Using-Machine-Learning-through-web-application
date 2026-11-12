
"""
Email service for NeuroCardioAI.

Uses Flask configuration for SMTP credentials.
Supports HTML emails, plain-text alternatives and attachments.
"""

import os
import html
import logging
import smtplib

from datetime import datetime

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

from flask import current_app, url_for


logger = logging.getLogger(__name__)


class EmailService:
    """Email service for NeuroCardioAI."""

    def __init__(self):
        """Initialize the email service."""
        pass

    # --------------------------------------------------
    # Send email
    # --------------------------------------------------

    def send_email(
        self,
        to_email,
        subject,
        html_body,
        attachments=None
    ):
        """
        Send an email with HTML and plain-text content.

        SMTP credentials are read from Flask configuration.
        """

        try:

            # Read configuration from Flask
            smtp_server = current_app.config.get(
                'MAIL_SERVER', 'smtp.gmail.com'
            )

            smtp_port = current_app.config.get(
                'MAIL_PORT', 587
            )

            username = current_app.config.get('MAIL_USERNAME')

            password = current_app.config.get('MAIL_PASSWORD')

            use_tls = current_app.config.get(
                'MAIL_USE_TLS', True
            )

            sender = (
                current_app.config.get('MAIL_DEFAULT_SENDER')
                or username
            )

            if not username or not password:
                logger.error(
                    "Email credentials are not configured."
                )
                return False

            if not to_email:
                logger.error("Recipient email is missing.")
                return False

            logger.info(
                "Attempting to send email to %s", to_email
            )

            # Create email message
            msg = MIMEMultipart('mixed')

            msg['From'] = sender
            msg['To'] = to_email
            msg['Subject'] = subject

            # Create alternative plain-text and HTML content
            alternative = MIMEMultipart('alternative')

            text_body = (
                "Please view this email in an "
                "HTML-compatible email client.\n\n"
                f"Subject: {subject}"
            )

            alternative.attach(
                MIMEText(text_body, 'plain', 'utf-8')
            )

            alternative.attach(
                MIMEText(html_body, 'html', 'utf-8')
            )

            msg.attach(alternative)

            # Attach files if provided.
            if attachments:

                for file_path in attachments:

                    if not os.path.isfile(file_path):
                        logger.warning(
                            "Attachment not found: %s",
                            file_path
                        )
                        continue

                    with open(file_path, 'rb') as file:

                        attachment = MIMEApplication(
                            file.read()
                        )

                    attachment.add_header(
                        'Content-Disposition',
                        'attachment',
                        filename=os.path.basename(file_path)
                    )

                    msg.attach(attachment)

            # Connect to SMTP server and send
            logger.info(
                "Connecting to SMTP server %s:%s",
                smtp_server,
                smtp_port
            )

            with smtplib.SMTP(
                smtp_server,
                smtp_port,
                timeout=20
            ) as server:

                server.ehlo()

                if use_tls:
                    server.starttls()
                    server.ehlo()

                logger.info("Logging in to SMTP server.")

                server.login(username, password)

                server.send_message(msg)

            logger.info(
                "Email successfully sent to %s",
                to_email
            )

            return True

        except Exception:

            logger.exception("Error sending email.")

            return False

    # --------------------------------------------------
    # Send prediction report
    # --------------------------------------------------

    def send_prediction_report(
        self,
        user_email,
        prediction
    ):
        """
        Send a prediction report via email.

        This method should be called while a Flask
        request context is available because it uses url_for().
        """

        try:

            subject = (
                f"NeuroCardioAI - Stroke Prediction Report "
                f"#{prediction.id}"
            )

            # Determine risk color
            risk_color = {
                'Low': '#28a745',
                'Moderate': '#ffc107',
                'High': '#dc3545'
            }.get(
                prediction.risk_level,
                '#17a2b8'
            )

            # Safely retrieve patient information
            user = getattr(prediction, 'user', None)

            patient_name = (
                getattr(user, 'full_name', None)
                or getattr(user, 'username', None)
                or 'User'
            )

            safe_patient_name = html.escape(
                str(patient_name)
            )

            safe_risk_level = html.escape(
                str(prediction.risk_level)
            )

            safe_prediction_type = html.escape(
                str(prediction.prediction_type).title()
            )

            created_at = (
                getattr(prediction, 'created_at', None)
                or datetime.now()
            )

            report_date = created_at.strftime(
                '%B %d, %Y at %I:%M %p'
            )

            # Generate report URL inside request context
            report_url = url_for(
                'main.view_result',
                id=prediction.id,
                _external=True
            )

            safe_report_url = html.escape(
                report_url,
                quote=True
            )

            # HTML email body
            html_body = f"""
            <!DOCTYPE html>
            <html>

            <head>
                <style>

                    body {{
                        font-family: Arial, sans-serif;
                    }}

                    .header {{
                        background: #4361ee;
                        color: white;
                        padding: 20px;
                        text-align: center;
                    }}

                    .risk-box {{
                        background: {risk_color};
                        color: white;
                        padding: 15px;
                        border-radius: 5px;
                        margin: 20px 0;
                        text-align: center;
                    }}

                    .info {{
                        background: #f8f9fa;
                        padding: 15px;
                        border-radius: 5px;
                    }}

                    .button {{
                        display: inline-block;
                        background: #4361ee;
                        color: white;
                        padding: 10px 20px;
                        text-decoration: none;
                        border-radius: 5px;
                    }}

                </style>
            </head>

            <body>

                <div class="header">
                    <h2>NeuroCardioAI</h2>
                    <p>Stroke Prediction Report</p>
                </div>

                <div class="risk-box">

                    <h2>
                        {prediction.risk_score:.1f}% Risk
                    </h2>

                    <p>
                        Risk Level:
                        <strong>{safe_risk_level}</strong>
                    </p>

                </div>

                <div class="info">

                    <p>
                        <strong>Report ID:</strong>
                        #{prediction.id}
                    </p>

                    <p>
                        <strong>Date:</strong>
                        {report_date}
                    </p>

                    <p>
                        <strong>Patient:</strong>
                        {safe_patient_name}
                    </p>

                    <p>
                        <strong>Type:</strong>
                        {safe_prediction_type} Stroke
                    </p>

                </div>

                <p style="margin-top: 25px;">

                    <a href="{safe_report_url}" class="button">
                        View Full Report
                    </a>

                </p>

                <p style="font-size: 12px; color: #666;">
                    Automated message from NeuroCardioAI.
                    Please do not reply.
                </p>

            </body>

            </html>
            """

            return self.send_email(
                user_email,
                subject,
                html_body
            )

        except Exception:

            logger.exception(
                "Failed to prepare prediction report email."
            )

            return False

    # --------------------------------------------------
    # Send test email
    # --------------------------------------------------

    def send_test_email(self, to_email):
        """Send a simple test email."""

        subject = "NeuroCardioAI - Test Email"

        body = f"""
        <h2>Test Email from NeuroCardioAI</h2>

        <p>
            If you're seeing this, email configuration
            is working correctly!
        </p>

        <p>
            Time:
            {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </p>
        """

        return self.send_email(
            to_email,
            subject,
            body
        )


# --------------------------------------------------
# Service access functions
# --------------------------------------------------

def get_email_service():
    """Create an email service instance."""

    return EmailService()


def send_prediction_report_email(
    user_email,
    prediction
):
    """Send prediction report."""

    service = get_email_service()

    return service.send_prediction_report(
        user_email,
        prediction
    )


def send_test_email(user_email):
    """Send test email."""

    service = get_email_service()

    return service.send_test_email(user_email)
