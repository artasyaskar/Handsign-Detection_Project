# Use an official Python runtime as a parent image
FROM python:3.9-slim-bullseye

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
# We'll update package lists and install dependencies in a single RUN command to reduce layers
# libgtk-3-0 and libgstreamer-plugins-base1.0-0 are runtime versions.
# If build issues arise with opencv or mediapipe, we might need dev versions like libgtk-3-dev.
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libx11-6 \
    libgtk-3-0 \
    libgstreamer-plugins-base1.0-0 \
    libegl1-mesa \
    ffmpeg \
    libsm6 \
    libxext6 \
    # Clean up apt caches to reduce image size
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose the port the app runs on. Fly.io will provide a PORT environment variable (typically 8080),
# which Gunicorn will use. This EXPOSE line is more for documentation.
EXPOSE 8080

# Command to run the application using Gunicorn
# Fly.io provides the PORT environment variable. Gunicorn will listen on this port.
# The number of workers can be adjusted based on the resources available on Railway.
# For now, using a default of 2 workers.
# The --timeout flag can be important for longer processing tasks if your /detect endpoint takes time.
CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "--workers", "2", "--timeout", "120", "app:app"]
