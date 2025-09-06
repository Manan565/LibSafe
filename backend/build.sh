
#!/usr/bin/env bash
# build.sh

set -o errexit  # exit on error

echo "🚀 Starting build process..."

# Upgrade pip
pip install --upgrade pip

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Download YOLO files (since they're too large for git)
echo "📥 Downloading YOLO model files..."

# Download yolov4.cfg
curl -o yolov4.cfg https://raw.githubusercontent.com/AlexeyAB/darknet/master/cfg/yolov4.cfg

# Download coco.names  
curl -o coco.names https://raw.githubusercontent.com/AlexeyAB/darknet/master/data/coco.names

# Download yolov4.weights (this is large ~245MB)
echo "📥 Downloading YOLO weights (this may take a few minutes)..."
curl -L -o yolov4.weights https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v4_pre/yolov4.weights

echo "✅ Build process completed!"