"""
Logging configuration for NeuroCardioAI - Fixed for Windows encoding
"""

import os
import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from datetime import datetime

def setup_logger(app):
    """Setup application logging"""
    
    # Create logs directory if not exists
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    # Set up formatters (remove special characters)
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Main application log
    app_log_handler = RotatingFileHandler(
        'logs/app.log', maxBytes=10485760, backupCount=10, encoding='utf-8'
    )
    app_log_handler.setFormatter(detailed_formatter)
    app_log_handler.setLevel(logging.INFO)
    
    # Prediction specific log
    pred_log_handler = TimedRotatingFileHandler(
        'logs/prediction.log', when='midnight', interval=1, backupCount=30, encoding='utf-8'
    )
    pred_log_handler.setFormatter(simple_formatter)
    pred_log_handler.setLevel(logging.INFO)
    
    # MRI analysis log
    mri_log_handler = TimedRotatingFileHandler(
        'logs/mri_gradcam.log', when='midnight', interval=1, backupCount=30, encoding='utf-8'
    )
    mri_log_handler.setFormatter(simple_formatter)
    mri_log_handler.setLevel(logging.INFO)
    
    # Error log
    error_log_handler = RotatingFileHandler(
        'logs/error.log', maxBytes=10485760, backupCount=10, encoding='utf-8'
    )
    error_log_handler.setFormatter(detailed_formatter)
    error_log_handler.setLevel(logging.ERROR)
    
    # Add handlers to app logger
    app.logger.addHandler(app_log_handler)
    app.logger.addHandler(error_log_handler)
    
    # Add handlers to specific loggers
    prediction_logger = logging.getLogger('prediction')
    prediction_logger.addHandler(pred_log_handler)
    prediction_logger.setLevel(logging.INFO)
    
    mri_logger = logging.getLogger('mri_analysis')
    mri_logger.addHandler(mri_log_handler)
    mri_logger.setLevel(logging.INFO)
    
    # Set console logging for development (handle Windows encoding)
    if app.debug:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(simple_formatter)
        # Use a filter to remove special characters for console
        console_handler.addFilter(lambda record: setattr(record, 'msg', 
            record.msg.replace('✓', '[OK]').replace('✗', '[ERROR]')) or True)
        app.logger.addHandler(console_handler)
    
    app.logger.info('NeuroCardioAI logging initialized')