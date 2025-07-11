# Use python:3.10-slim as the base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsm6 \
    libxext6 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy static and template folders if they exist
# (Assuming they are in the build context root, alongside Dockerfile)
COPY static ./static
COPY templates ./templates

# Copy the application code
COPY api/flask_app.py .

# Set the PORT environment variable (though vercel.json also sets this for the Vercel build environment)
ENV PORT=8080

# Expose port 8080
EXPOSE 8080

# Define the command to run the Flask app
CMD ["python", "flask_app.py"]
