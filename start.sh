#!/bin/bash
set -e

echo "Starting face detection application..."

# Check if database environment variables are set
if [ -z "$DATABASE_URI" ]; then
  echo "WARNING: DATABASE_URI is not set, using default SQLite database"
fi

# Start gunicorn with the application
exec gunicorn --bind 0.0.0.0:5000 wsgi:app
