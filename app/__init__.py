#!/usr/bin/env python3

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-please-change')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI', 'sqlite:////tmp/images.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER', os.path.join(app.root_path, 'static/uploads'))
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size
    app.config['SKYBIOMETRY_API_KEY'] = os.environ.get('SKYBIOMETRY_API_KEY', '')
    app.config['SKYBIOMETRY_API_SECRET'] = os.environ.get('SKYBIOMETRY_API_SECRET', '')
    app.config['MAIL_RELAY_HOST'] = os.environ.get('MAIL_RELAY_HOST', 'postfix-relay.mail.svc.cluster.local')
    app.config['MAIL_RELAY_PORT'] = int(os.environ.get('MAIL_RELAY_PORT', '25'))
    
    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Initialize extensions
    db.init_app(app)
    
    # Register blueprints
    from app.routes import main
    app.register_blueprint(main)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app
