
"""
NeuroCardioAI Main Application
Hospital-themed stroke prediction system
"""

import os
import logging
from datetime import datetime

from dotenv import load_dotenv

# --------------------------------------------------
# Load environment variables BEFORE importing config
# --------------------------------------------------

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
dotenv_path = os.path.join(BASE_DIR, '.env')

load_dotenv(dotenv_path=dotenv_path)

# --------------------------------------------------
# Local imports
# --------------------------------------------------

from flask import (
    Flask,
    render_template,
    jsonify
)

from config import config
from extensions import db, login_manager
from utils.logger import setup_logger


# --------------------------------------------------
# Application factory
# --------------------------------------------------

def create_app(config_name='default'):

    """Create and configure the Flask application."""

    # Validate configuration name
    if config_name not in config:
        raise ValueError(
            f"Invalid configuration name: {config_name}"
        )

    app = Flask(__name__)

    # Load configuration
    app.config.from_object(config[config_name])

    # Ensure SECRET_KEY is configured
    if not app.config.get('SECRET_KEY'):
        raise RuntimeError(
            "SECRET_KEY is missing. Please configure it in your .env file."
        )

    # --------------------------------------------------
    # Initialize extensions
    # --------------------------------------------------

    db.init_app(app)

    login_manager.init_app(app)

    login_manager.login_view = 'auth.login'

    login_manager.login_message = (
        'Please login to access this page'
    )

    login_manager.login_message_category = 'warning'

    # --------------------------------------------------
    # Setup logging
    # --------------------------------------------------

    setup_logger(app)

    # --------------------------------------------------
    # Import models
    # --------------------------------------------------

    from database.models import User

    @login_manager.user_loader
    def load_user(user_id):

        return User.query.get(int(user_id))

    # --------------------------------------------------
    # Register blueprints
    # --------------------------------------------------

    from api.routes import main_bp
    from api.prediction_api import prediction_bp
    from api.mri_api import mri_bp
    from api.auth_routes import auth_bp
    from api.admin_routes import admin_bp

    app.register_blueprint(main_bp)

    app.register_blueprint(
        prediction_bp,
        url_prefix='/api'
    )

    app.register_blueprint(
        mri_bp,
        url_prefix='/mri'
    )

    app.register_blueprint(
        auth_bp,
        url_prefix='/auth'
    )

    app.register_blueprint(
        admin_bp,
        url_prefix='/admin'
    )

    # --------------------------------------------------
    # Custom template filters
    # --------------------------------------------------

    @app.template_filter('datetime')
    def datetime_filter(value, format='%Y-%m-%d %H:%M'):

        if value is None:
            return ""

        return value.strftime(format)

    @app.template_filter('risk_color')
    def risk_color_filter(risk):

        if isinstance(risk, str):

            if risk.lower() == 'low':
                return 'success'

            elif risk.lower() == 'moderate':
                return 'warning'

            elif risk.lower() == 'high':
                return 'danger'

            return 'secondary'

        try:

            if risk < 30:
                return 'success'

            elif risk < 60:
                return 'warning'

            else:
                return 'danger'

        except (TypeError, ValueError):
            return 'secondary'

    @app.template_filter('format_number')
    def format_number_filter(value, decimals=1):

        try:
            return f"{value:.{decimals}f}"

        except (TypeError, ValueError):
            return str(value)

    # --------------------------------------------------
    # Context processor
    # --------------------------------------------------

    @app.context_processor
    def utility_processor():

        return {
            'now': datetime.now(),
            'app_name': 'NeuroCardioAI',
            'hospital_name': 'NeuroCardio Medical Center',
            'current_year': datetime.now().year
        }

    # --------------------------------------------------
    # Error handlers
    # --------------------------------------------------

    @app.errorhandler(404)
    def not_found_error(error):

        return render_template(
            'errors/404.html'
        ), 404

    @app.errorhandler(500)
    def internal_error(error):

        db.session.rollback()

        return render_template(
            'errors/500.html'
        ), 500

    # --------------------------------------------------
    # Health check endpoint
    # --------------------------------------------------

    @app.route('/health')
    def health_check():

        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '2.0.0'
        }), 200

    return app


# --------------------------------------------------
# Create application instance
# --------------------------------------------------

app = create_app(
    os.getenv('FLASK_CONFIG', 'default')
)


# --------------------------------------------------
# Run application
# --------------------------------------------------

if __name__ == '__main__':

    app.run(
        debug=app.config.get('DEBUG', False),
        host='0.0.0.0',
        port=5000
    )
