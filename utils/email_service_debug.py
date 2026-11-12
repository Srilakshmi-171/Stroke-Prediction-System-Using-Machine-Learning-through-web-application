
"""
Debug email service to test email functionality.

Uses Flask configuration for SMTP credentials.
"""

import logging
import smtplib

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from flask import current_app


logger = logging.getLogger(__name__)


def send_debug_email(to_email, subject, message):
    """Send a simple debug email using Flask configuration."""

    try:

        # ------------------------------------------
        # Read email configuration
        # ------------------------------------------

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

        # ------------------------------------------
        # Validate configuration
        # ------------------------------------------

        if not username or not password:
            logger.error(
                "Email credentials are not configured."
            )
            return False

        if not to_email:
            logger.error("Recipient email is missing.")
            return False

        logger.info(
            "Attempting debug email to %s", to_email
        )

        # ------------------------------------------
        # Create email message
        # ------------------------------------------

        msg = MIMEMultipart()

        msg['From'] = sender
        msg['To'] = to_email
        msg['Subject'] = subject

        msg.attach(
            MIMEText(message, 'plain', 'utf-8')
        )

        # ------------------------------------------
        # Connect and send email
        # ------------------------------------------

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

            logger.info("Sending debug email.")

            server.send_message(msg)

        logger.info(
            "Debug email sent successfully to %s",
            to_email
        )

        return True

    except Exception:

        logger.exception("Debug email sending failed.")

        return False


def test_simple_email(to_email):
    """
    Send a test email to the supplied recipient.

    Pass the recipient explicitly instead of hardcoding
    an email address in the source code.
    """

    return send_debug_email(
        to_email=to_email,
        subject='NeuroCardioAI Debug Test',
        message=(
            'This is a test email from the '
            'NeuroCardioAI debug system.'
        )
    )
