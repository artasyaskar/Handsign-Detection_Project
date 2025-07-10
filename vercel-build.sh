#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

echo ">>> Installing system dependencies..."

# Update yum and install dependencies
# -y automatically assumes "yes" to all prompts
sudo yum update -y
sudo yum install -y mesa-libGL libX11 gtk3-devel gstreamer-plugins-base-devel mesa-libEGL

echo ">>> System dependencies installed."

echo ">>> Installing Python dependencies from requirements.txt..."
pip install -r requirements.txt

echo ">>> Python dependencies installed."
echo ">>> Build script finished."
