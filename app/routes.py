#!/usr/bin/env python3

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
import os
import uuid
from werkzeug.utils import secure_filename
from app.models import Image, Subscriber
from app import db
from app.face_detection import SkybiometryFaceDetection
from app.email_service import EmailService

main = Blueprint('main', __name__)

# Helper functions
def allowed_file(filename):
    """Check if the file has an allowed extension."""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main.route('/')
def index():
    """Home page with upload form and recent images."""
    images = Image.query.order_by(Image.upload_date.desc()).limit(10).all()
    return render_template('index.html', images=images)

@main.route('/upload', methods=['POST'])
def upload():
    """Handle image upload and face detection."""
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        # Generate a unique filename
        filename = str(uuid.uuid4()) + secure_filename(file.filename)
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        
        # Save the file
        file.save(filepath)
        
        # Get description
        description = request.form.get('description', '')
        
        # Create new image record
        new_image = Image(
            filename=filename,
            description=description,
            faces_detected=0
        )
        
        # Detect faces
        face_detector = SkybiometryFaceDetection(
            current_app.config['SKYBIOMETRY_API_KEY'],
            current_app.config['SKYBIOMETRY_API_SECRET']
        )
        
        try:
            # Detect faces and store the data
            faces = face_detector.detect_faces(filepath)
            new_image.set_faces(faces)
            
            # Save image info to database
            db.session.add(new_image)
            db.session.commit()
            
            # Send notifications if faces were detected
            if new_image.faces_detected > 0:
                email_service = EmailService(
                    current_app.config['MAIL_RELAY_HOST'],
                    current_app.config['MAIL_RELAY_PORT']
                )
                
                image_url = url_for('main.view_image', image_id=new_image.id, _external=True)
                unsubscribe_url = url_for('main.unsubscribe', _external=True)
                
                image_data = {
                    'description': description,
                    'faces_detected': new_image.faces_detected,
                    'url': image_url,
                    'unsubscribe_url': unsubscribe_url
                }
                
                email_service.send_notification(image_data)
            
            flash(f'Image uploaded successfully! Detected {new_image.faces_detected} faces.')
            return redirect(url_for('main.view_image', image_id=new_image.id))
            
        except Exception as e:
            flash(f'Error detecting faces: {str(e)}')
            return redirect(url_for('main.index'))
    
    flash('Invalid file type')
    return redirect(url_for('main.index'))

@main.route('/image/<int:image_id>')
def view_image(image_id):
    """Display an image with detected faces."""
    image = Image.query.get_or_404(image_id)
    
    # Get face data from the database instead of making an API call
    faces = image.get_faces()
    
    return render_template('view.html', image=image, faces=faces)

@main.route('/subscribe', methods=['POST'])
def subscribe():
    """Subscribe to notifications for new images."""
    email = request.form.get('email')
    
    if not email:
        flash('Email is required')
        return redirect(url_for('main.index'))
    
    # Check if already subscribed
    existing = Subscriber.query.filter_by(email=email).first()
    if existing:
        if existing.active:
            flash('You are already subscribed')
        else:
            existing.active = True
            db.session.commit()
            flash('Your subscription has been reactivated')
    else:
        # Add new subscriber
        new_subscriber = Subscriber(email=email)
        db.session.add(new_subscriber)
        db.session.commit()
        flash('You have been subscribed to notifications')
    
    return redirect(url_for('main.index'))

@main.route('/unsubscribe', methods=['GET', 'POST'])
def unsubscribe():
    """Unsubscribe from notifications."""
    if request.method == 'POST':
        email = request.form.get('email')
        
        if not email:
            flash('Email is required')
            return render_template('unsubscribe.html')
        
        subscriber = Subscriber.query.filter_by(email=email).first()
        if subscriber:
            subscriber.active = False
            db.session.commit()
            flash('You have been unsubscribed')
        else:
            flash('Email not found in our subscribers list')
        
        return redirect(url_for('main.index'))
    
    return render_template('unsubscribe.html')

@main.route('/images')
def list_images():
    """List all uploaded images."""
    images = Image.query.order_by(Image.upload_date.desc()).all()
    return render_template('list.html', images=images)

@main.route('/health')
def health_check():
    """Health check endpoint that verifies database connectivity."""
    try:
        # Execute a simple query to check database connectivity
        db.session.execute('SELECT 1')
        return {
            'status': 'healthy',
            'database': 'connected'
        }, 200
    except Exception as e:
        return {
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e)
        }, 500
