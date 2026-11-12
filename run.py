#!/usr/bin/env python3
"""
NeuroCardioAI - Advanced Stroke Prediction System
Run this file to start the application
"""

import os
import sys
from app import app, db
from database.models import init_db

def create_directories():
    """Create necessary directories if they don't exist"""
    directories = [
        'database',
        'models',
        'static/uploads/mri',
        'static/heatmaps',
        'static/reports',
        'static/3d',
        'logs'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Created directory: {directory}")

def main():
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║   ███╗   ██╗███████╗██╗   ██╗██████╗  ██████╗           ║
    ║   ████╗  ██║██╔════╝██║   ██║██╔══██╗██╔═══██╗          ║
    ║   ██╔██╗ ██║█████╗  ██║   ██║██████╔╝██║   ██║          ║
    ║   ██║╚██╗██║██╔══╝  ██║   ██║██╔══██╗██║   ██║          ║
    ║   ██║ ╚████║███████╗╚██████╔╝██║  ██║╚██████╔╝          ║
    ║   ╚═╝  ╚═══╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝ ╚═════╝           ║
    ║                                                          ║
    ║              ██████╗ █████╗ ██╗                         ║
    ║             ██╔════╝██╔══██╗██║                         ║
    ║             ██║     ███████║██║                         ║
    ║             ██║     ██╔══██║██║                         ║
    ║             ╚██████╗██║  ██║██║                         ║
    ║              ╚═════╝╚═╝  ╚═╝╚═╝                         ║
    ║                                                          ║
    ║           Advanced Stroke Prediction System              ║
    ║                 Hospital Edition v2.0                    ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    print("\n[✓] Initializing NeuroCardioAI System...")
    
    # Create directories
    create_directories()
    
    # Initialize database
    with app.app_context():
        init_db()
        print("[✓] Database initialized successfully")
    
    # Start the application
    print(f"\n[✓] System ready! Starting server on http://127.0.0.1:5000")
    print("[✓] Press Ctrl+C to stop the server\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    main()