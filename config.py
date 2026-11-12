import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Basic Flask config
    SECRET_KEY = os.environ.get('SECRET_KEY')
    DEBUG = True
    TESTING = False
    
    # Database
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'database', 'database.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session config
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    REMEMBER_COOKIE_DURATION = timedelta(days=7)
    
    # Upload folders
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    MRI_UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads', 'mri')
    HEATMAP_FOLDER = os.path.join(BASE_DIR, 'static', 'heatmaps')
    REPORT_FOLDER = os.path.join(BASE_DIR, 'static', 'reports')
    
    # Allowed extensions
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'dcm'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload
    
    # Model paths
    MODELS_PATH = os.path.join(BASE_DIR, 'models')
    
    # Email config (for reports)
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')  # Should be set in .env file
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')  # Should be set in .env file
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@neurocardio.com')
    BASE_URL = os.environ.get('BASE_URL', 'http://localhost:5000')
    
    # Redis config for Celery
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    
    # API Keys
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')  # For enhanced recommendations

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}