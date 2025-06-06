#!/usr/bin/env python3

import requests
import os
import logging
from urllib.parse import urlencode

logger = logging.getLogger(__name__)

class SkybiometryFaceDetection:
    """
    A wrapper class for the Skybiometry Face Detection API.
    """
    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://api.skybiometry.com/fc/faces/detect"
    
    def detect_faces(self, image_path):
        """
        Detects faces in an image and returns the coordinates.
        
        Args:
            image_path: The local path to the image
            
        Returns:
            A list of dictionaries containing face coordinates (x, y, width, height)
        """
        params = {
            'api_key': self.api_key,
            'api_secret': self.api_secret,
            'attributes': 'all',
        }
        
        with open(image_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(
                self.base_url, 
                params=params,
                files=files
            )
        
        if response.status_code != 200:
            raise Exception(f"API request failed with status {response.status_code}: {response.text}")
        
        data = response.json()
        
        # Check for API errors
        if data.get('status') != 'success':
            error_msg = data.get('error_message', 'Unknown error')
            raise Exception(f"API error: {error_msg}")
        
        # Extract face coordinates
        faces = []
        
        # Debug logging
        logger.debug(f"API Response: {data}")
        
        if 'photos' in data and data['photos']:
            photo = data['photos'][0]
            if 'tags' in photo:
                for tag in photo['tags']:
                    # Extract face coordinates from the tag
                    face = {
                        'x': tag['center']['x'],
                        'y': tag['center']['y'],
                        'width': tag['width'],
                        'height': tag['height']
                    }
                    
                    # Debug log the face we're adding
                    logger.debug(f"Adding face: {face}")
                    
                    faces.append(face)
        
        # Log the number of faces detected
        logger.info(f"Detected {len(faces)} faces in the image")
        
        return faces
