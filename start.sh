#!/bin/bash
set -e

echo "Starting face detection application..."

# Check if PostgreSQL environment variables are set
if [ -n "$POSTGRES_USER" ] && [ -n "$POSTGRES_PASSWORD" ]; then
  echo "PostgreSQL environment variables found, will attempt to use PostgreSQL"
else
  echo "WARNING: PostgreSQL environment variables not set, using default SQLite database"
fi

# Start gunicorn with the application
exec gunicorn --bind 0.0.0.0:5000 wsgi:app
