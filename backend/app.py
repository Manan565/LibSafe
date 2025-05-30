from flask import Flask, Response, request, jsonify
import cv2
import numpy as np
import os
import time
import threading
from flask_cors import CORS
from object_detector import ObjectDetector
from notifier import Notifier

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize detector and notifier
detector = ObjectDetector(confidence_threshold=0.6, sensitivity=40.0)
notifier = Notifier()

# Global variables
camera = None
is_monitoring = False
monitoring_thread = None
target_objects = ["laptop", "backpack", "book", "cell phone", "bottle", "umbrella"]
student_phone = None
recent_notifications = []
frame_count = 0

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get current monitoring status."""
    global is_monitoring, student_phone
    return jsonify({
        "is_monitoring": is_monitoring,
        "student_phone": student_phone,
        "timestamp": time.time()
    })

@app.route('/api/test', methods=['GET'])
def test_route():
    """Simple test route to verify backend is working."""
    global is_monitoring, student_phone
    return jsonify({
        "message": "Backend is working", 
        "is_monitoring": is_monitoring,
        "student_phone": student_phone,
        "timestamp": time.time()
    })

@app.route('/api/stop', methods=['POST'])
def stop_monitoring():
    """Stop the monitoring process."""
    global camera, is_monitoring, student_phone
    
    print("🛑 Stopping monitoring...")
    is_monitoring = False
    student_phone = None
    print(f"MONITORING DEACTIVATED - is_monitoring: {is_monitoring}, student_phone: {student_phone}")
    
    return jsonify({"success": True, "message": "Monitoring stopped successfully"})

@app.route('/api/check_notifications')
def check_notifications():
    """Return recent notifications for browserm."""
    current_time = time.time()
    recent = [n for n in recent_notifications if current_time - n["timestamp"] < 30]
    
    if recent:
        print(f"📋 Returning {len(recent)} notifications to browser")
    
    return jsonify({
        "notifications": recent
    })

@app.route('/api/start', methods=['POST'])
def start_monitoring():
    """Start the monitoring process."""
    global camera, is_monitoring, student_phone, monitoring_thread
    
    print("🚀 START ROUTE CALLED!")
    print(f"📝 Request method: {request.method}")
    print(f"📄 Request headers: {dict(request.headers)}")
    
    try:
        data = request.get_json()
        print(f"📦 Raw request data: {data}")
        
        if data is None:
            print("❌ No JSON data received")
            return jsonify({"success": False, "message": "No data received"}), 400
        
        phone = data.get('phone')
        print(f"📞 Extracted phone: {phone}")
        
