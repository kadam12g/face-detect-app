#!/usr/bin/env python3

import requests
import os
from urllib.parse import urlencode

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
        if 'photos' in data and data['photos']:
            photo = data['photos'][0]
            if 'tags' in photo:
                for tag in photo['tags']:
                    face = {
                        'x': tag['center']['x'],
                        'y': tag['center']['y'],
                        'width': tag['width'],
                        'height': tag['height']
                    }
                    faces.append(face)
        
        return faces
