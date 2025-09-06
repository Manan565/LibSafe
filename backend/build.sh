#!/usr/bin/env bash
# build.sh

set -o errexit  # exit on error

echo "Starting build process..."

# Upgrade pip and setuptools
pip install --upgrade pip setuptools wheel

# Install Python dependencies with no cache to avoid conflicts
echo "Installing Python dependencies..."
pip install --no-cache-dir -r requirements.txt

# Download YOLO files (since they're too large for git)
echo "Downloading YOLO model files..."

# Download yolov4.cfg
echo "Downloading yolov4.cfg..."
curl -f -o yolov4.cfg https://raw.githubusercontent.com/AlexeyAB/darknet/master/cfg/yolov4.cfg || echo "Failed to download yolov4.cfg"

# Download coco.names  
echo "Downloading coco.names..."
curl -f -o coco.names https://raw.githubusercontent.com/AlexeyAB/darknet/master/data/coco.names || echo "Failed to download coco.names"

# Download yolov4.weights (this is large ~245MB)
echo "Downloading YOLO weights (this may take a few minutes)..."
curl -f -L -o yolov4.weights https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v4_pre/yolov4.weights || echo "Failed to download yolov4.weights"

# Check if files were downloaded successfully
if [ -f "yolov4.cfg" ] && [ -f "coco.names" ] && [ -f "yolov4.weights" ]; then
    echo "All YOLO files downloaded successfully!"
    ls -la *.cfg *.names *.weights
else
    echo "Warning: Some YOLO files may not have downloaded correctly"
    ls -la
fi

echo "Build process completed!"