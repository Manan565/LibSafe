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
is_monitoring = False
target_objects = ["laptop", "backpack", "book", "cell phone", "bottle", "umbrella"]
student_phone = None
recent_notifications = []
last_movement_check = {}

@app.route('/', methods=['GET'])
def health_check():
    """Health check route for cloud deployment."""
    return jsonify({
        "status": "healthy",
        "message": "Library Safety Backend is running",
        "timestamp": time.time(),
        "environment": "cloud"
    })

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
    global is_monitoring, student_phone
    
    print("🛑 Stopping monitoring...")
    is_monitoring = False
    student_phone = None
    detector.reset()  # Reset detector state
    print(f"MONITORING DEACTIVATED - is_monitoring: {is_monitoring}, student_phone: {student_phone}")
    
    return jsonify({"success": True, "message": "Monitoring stopped successfully"})

@app.route('/api/start', methods=['POST'])
def start_monitoring():
    """Start the monitoring process."""
    global is_monitoring, student_phone
    
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

@app.route('/api/process-frame', methods=['POST'])
def process_frame():
    """Process individual frames sent from frontend camera."""
    global is_monitoring, student_phone, recent_notifications, last_movement_check
    
    print(f"🖼️ Frame processing request received")
    print(f"📊 Current state: is_monitoring={is_monitoring}, student_phone={student_phone}")
    
    if not is_monitoring or not student_phone:
        return jsonify({"error": "Monitoring not active", "is_monitoring": is_monitoring}), 400
    
    try:
        # Check if frame was uploaded
        if 'frame' not in request.files:
            print("❌ No frame in request.files")
            return jsonify({"error": "No frame received"}), 400
        
        frame_file = request.files['frame']
        phone = request.form.get('phone', student_phone)
        
        print(f"📱 Processing frame for phone: {phone}")
        print(f"📏 Frame file size: {len(frame_file.read())} bytes")
        frame_file.seek(0)  # Reset file pointer after reading size
        
        # Read frame data
        frame_bytes = np.frombuffer(frame_file.read(), np.uint8)
        frame = cv2.imdecode(frame_bytes, cv2.IMREAD_COLOR)
        
        if frame is None:
            print("❌ Failed to decode frame")
            return jsonify({"error": "Invalid frame data"}), 400
        
        print(f"🖼️ Frame decoded successfully: {frame.shape}")
        
        # Process frame with object detector
        processed_frame_bytes, movements = detector.process_frame(frame, target_objects)
        
        print(f"🎯 Detection results: {movements}")
        
        # Send notifications if movements detected
        current_time = time.time()
        notifications_sent = []
        
        if movements and phone:
            print(f"🚨 MOVEMENTS DETECTED: {movements}")
            
            for obj, action in movements.items():
                # Rate limiting: only send notifications every 30 seconds per object
                if obj not in last_movement_check or current_time - last_movement_check[obj] > 30:
                    message = f"LIBRARY SAFETY ALERT: Your {obj} has {action}! Please check your belongings."
                    
                    try:
                        print(f"📤 Sending notification for {obj}")
                        success_result, result = notifier.send_notification(phone, message)
                        
                        # Store notification
                        notification_record = {
                            "timestamp": current_time,
                            "message": message,
                            "success": success_result,
                            "object": obj,
                            "action": action
                        }
                        recent_notifications.append(notification_record)
                        notifications_sent.append(notification_record)
                        
                        print(f"📨 Notification sent for {obj}: success={success_result}")
                        
                        # Update last notification time for this object
                        last_movement_check[obj] = current_time
                        
                        # Keep only recent notifications (last 10)
                        if len(recent_notifications) > 10:
                            recent_notifications.pop(0)
                            
                    except Exception as e:
                        print(f"❌ Notification error for {obj}: {e}")
                        import traceback
                        traceback.print_exc()
                else:
                    print(f"⏱️ Skipping notification for {obj} (rate limited)")
        
        return jsonify({
            "success": True,
            "movements_detected": movements,
            "objects_found": list(movements.keys()) if movements else [],
            "notifications_sent": len(notifications_sent),
            "timestamp": time.time(),
            "monitoring_active": is_monitoring
        })
        
    except Exception as e:
        print(f"❌ Frame processing error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Processing failed: {str(e)}"}), 500

@app.route('/api/check_notifications')
def check_notifications():
    """Return recent notifications for browser."""
    current_time = time.time()
    recent = [n for n in recent_notifications if current_time - n["timestamp"] < 60]  # Last 60 seconds
    
    if recent:
        print(f"📋 Returning {len(recent)} notifications to browser")
    
    return jsonify({
        "notifications": recent,
        "count": len(recent),
        "timestamp": current_time
    })

# Keep the old video_feed endpoint for demo purposes (shows static demo)
@app.route('/api/video_feed')
def video_feed():
    """Demo video feed for cloud deployment - shows placeholder."""
    def generate_demo_frames():
        while True:
            # Create demo frame
            demo_frame = np.zeros((480, 640, 3), dtype=np.uint8)
            
            # Add demo content
            cv2.putText(demo_frame, 'CLOUD DEPLOYMENT MODE', (150, 200), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.putText(demo_frame, 'Camera runs in browser', (180, 250), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(demo_frame, 'Frames sent to backend for processing', (120, 300), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Add timestamp
            timestamp = time.strftime("%H:%M:%S")
            cv2.putText(demo_frame, f'Server Time: {timestamp}', (200, 350), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            ret, frame_bytes = cv2.imencode('.jpg', demo_frame)
            yield (b'--frame\r\n'
                  b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes.tobytes() + b'\r\n')
            time.sleep(1)  # Slow refresh for demo
    
    return Response(generate_demo_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    # Get port from environment variable (Render/Heroku provides this)
    port = int(os.environ.get('PORT', 5000))
    
    print("🚀 Starting Flask application...")
    print(f"🌐 Running on port: {port}")
    print("🎯 Mode: Cloud-ready (frontend camera)")
    print("Press CTRL+C to stop the server")
    
    # Use 0.0.0.0 to accept connections from any IP
    app.run(debug=False, host='0.0.0.0', port=port)