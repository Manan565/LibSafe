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
    
        
        if not phone or not phone.strip():
            print("❌ Phone number validation failed")
            return jsonify({"success": False, "message": "Phone number is required"}), 400
        
        # Format phone number (simple validation)
        phone = phone.strip()
        if not phone.startswith('+'):
            phone = '+' + phone
        
        print(f"📱 Formatted phone: {phone}")
        
        # CRITICAL: Set these BEFORE any other operations
        student_phone = phone
        is_monitoring = True
        
        print(f"✅ MONITORING ACTIVATED!")
        print(f"📱 Phone: {student_phone}")
        print(f"🚨 is_monitoring: {is_monitoring}")
        
        # Reset detector
        detector.reset()
        print("🔄 Detector reset")
        return jsonify({"success": True, "message": "Monitoring started successfully"})
        
    except Exception as e:
        print(f"❌ ERROR in start_monitoring: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500

@app.route('/api/video_feed')
def video_feed():
    """Video streaming generator function that handles both display and monitoring."""
    def generate_frames():
        global camera, frame_count, is_monitoring, student_phone
        
        print("📹 Video feed started")
        
        # Initialize camera in this thread
        camera = None
        last_movement_check = time.time()
        
        # Try to open camera
        for camera_index in [0, 1]:
            print(f"📷 Video feed: Trying camera {camera_index}")
            camera = cv2.VideoCapture(camera_index)
            if camera.isOpened():
                print(f"✅ Video feed: Camera {camera_index} opened successfully")
                break
            else:
                camera = None
        
        if camera is None:
            print("❌ Video feed: Failed to open any camera")
            while True:
                placeholder_frame = np.zeros((480, 640, 3), dtype=np.uint8)
                cv2.putText(placeholder_frame, 'Camera not available', (150, 240), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                
                ret, frame_bytes = cv2.imencode('.jpg', placeholder_frame)
                yield (b'--frame\r\n'
                      b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes.tobytes() + b'\r\n')
                time.sleep(0.1)
        
        # Main video loop
        while True:
            success, frame = camera.read()
            if not success:
                print("❌ Video feed: Failed to grab frame")
                break
            
            frame_count += 1
            current_time = time.time()
            
            # Process frame with object detection for display
            processed_frame, movements = detector.process_frame(frame, target_objects)
            
            # CHECK MONITORING STATE EVERY FRAME (not cached)
            current_is_monitoring = is_monitoring
            current_student_phone = student_phone

            # Only log movements if they exist
            if movements:
                print(f"🎯 Frame {frame_count}: movements detected = {movements}")
                print(f"🔍 FRESH State Check: is_monitoring={current_is_monitoring}, student_phone={current_student_phone}")
            
            # Check for notifications (using fresh state every time)
            if (movements and current_is_monitoring and current_student_phone is not None and 
                current_time - last_movement_check > 2.0):
                
                print(f"🚨🚨🚨 SENDING NOTIFICATION! 🚨🚨🚨")
                print(f"📊 Movement details: {movements}")
                
                for obj, action in movements.items():
                    message = f"LIBRARY SAFETY ALERT: Your {obj} has {action}! Please check your belongings."
                    print(f"📤 Sending notification to {current_student_phone}: {message}")
                    
                    try:
                        success_result, result = notifier.send_notification(current_student_phone, message)
                        print(f"📨 Notification result: success={success_result}, result={result}")
                        
                        # Store notification for browser polling
                        recent_notifications.append({
                            "timestamp": time.time(),
                            "message": message,
                            "success": success_result
                        })
                        print(f"💾 Stored notification. Total stored: {len(recent_notifications)}")
                        
                        # Keep only the 10 most recent notifications
                        if len(recent_notifications) > 10:
                            recent_notifications.pop(0)
                            
                    except Exception as e:
                        print(f"❌ ERROR in notification: {e}")
                        import traceback
                        traceback.print_exc()
                
                last_movement_check = current_time
            
            # Yield the processed frame
            yield (b'--frame\r\n'
                  b'Content-Type: image/jpeg\r\n\r\n' + processed_frame + b'\r\n')
            
            # Limit frame rate
            time.sleep(0.05)
        
        # Cleanup
        if camera is not None:
            camera.release()
            camera = None
    
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
