FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create uploads directory
RUN mkdir -p app/static/uploads && chmod 777 app/static/uploads

# Set environment variables
ENV FLASK_APP=app
ENV FLASK_ENV=production

# Run as non-root user for better security
RUN useradd -m appuser
USER appuser

# Run gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "wsgi:app"]
