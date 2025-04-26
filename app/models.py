#!/usr/bin/env python3

from app import db
from datetime import datetime
import json

class Image(db.Model):
    __tablename__ = 'images'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    faces_detected = db.Column(db.Integer, default=0)
    faces_data = db.Column(db.Text)  # Store face detection JSON data
    
    def get_faces(self):
        """Return the faces data as a Python object."""
        if self.faces_data:
            return json.loads(self.faces_data)
        return []
    
    def set_faces(self, faces):
        """Store faces data as JSON string."""
        self.faces_data = json.dumps(faces)
        self.faces_detected = len(faces)
    
    def __repr__(self):
        return f'<Image {self.filename}>'

class Subscriber(db.Model):
    __tablename__ = 'subscribers'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128), nullable=False, unique=True)
    subscription_date = db.Column(db.DateTime, default=datetime.utcnow)
    active = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<Subscriber {self.email}>'
