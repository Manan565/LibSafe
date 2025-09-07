from flask import Flask, request, jsonify
import os
import time
import json
from flask_cors import CORS
from google.cloud import vision
from google.oauth2 import service_account
from notifier import Notifier
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize Google Vision API client
def initialize_vision_client():
    try:
        # For cloud deployment (Render, Heroku, etc.)
        if os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON'):
            credentials_json = os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON')
            credentials_dict = json.loads(credentials_json)
            credentials = service_account.Credentials.from_service_account_info(credentials_dict)
            return vision.ImageAnnotatorClient(credentials=credentials)
        else:
            # For local development (uses GOOGLE_APPLICATION_CREDENTIALS env var)
            return vision.ImageAnnotatorClient()
    except Exception as e:
        print(f"Error initializing Vision API: {e}")
        return None

vision_client = initialize_vision_client()
notifier = Notifier()

# Global variables
is_monitoring = False
target_objects = ["laptop", "backpack", "book", "mobile phone", "bottle", "umbrella"]
student_phone = None
recent_notifications = []
last_movement_check = 0
previous_detections = []

def detect_objects_google(image_bytes):
    """Detect objects using Google Cloud Vision API."""
    if not vision_client:
        print("Vision API client not initialized")
        return []
    
    try:
        image = vision.Image(content=image_bytes)
        response = vision_client.object_localization(image=image)
        
        detected_objects = []
        for obj in response.localized_object_annotations:
            object_name = obj.name.lower()
            
            # Map Google Vision names to our target objects
            name_mapping = {
                'laptop': 'laptop',
                'computer': 'laptop',
                'backpack': 'backpack', 
                'bag': 'backpack',
                'handbag': 'backpack',
                'book': 'book',
                'mobile phone': 'mobile phone',
                'cell phone': 'mobile phone',
                'bottle': 'bottle',
                'umbrella': 'umbrella'
            }
            
            # Check if detected object matches our targets
            mapped_name = None
            for key, value in name_mapping.items():
                if key in object_name:
                    mapped_name = value
                    break
            
            if mapped_name and obj.score > 0.5:  # 50% confidence threshold
                detected_objects.append({
                    'label': mapped_name,
                    'confidence': obj.score
                })
        
        return detected_objects
        
    except Exception as e:
        print(f"Error in Google Vision API: {e}")
        return []

def calculate_movement(current_detections):
    """Calculate if objects have disappeared."""
    global previous_detections
    
    # If no previous detections, establish baseline
    if not previous_detections:
        previous_detections = current_detections
        if current_detections:
            detected_labels = [d['label'] for d in current_detections]
            print(f"Baseline established with objects: {detected_labels}")
        else:
            print("Baseline established - no objects detected")
        return {}
    
    movements = {}
    
    # Create sets of detected object labels
    prev_objects = {d['label'] for d in previous_detections}
    curr_objects = {d['label'] for d in current_detections}
    
    # Check for disappeared objects
    disappeared_objects = prev_objects - curr_objects
    
    for obj in disappeared_objects:
        movements[obj] = "disappeared"
        print(f"OBJECT DISAPPEARED: {obj}")
    
    # Update previous detections
    previous_detections = current_detections
    
    return movements

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get current monitoring status."""
    global is_monitoring, student_phone
    return jsonify({
        "is_monitoring": is_monitoring,
        "student_phone": student_phone,
        "vision_api_ready": vision_client is not None,
        "timestamp": time.time()
    })

@app.route('/api/test', methods=['GET'])
def test_route():
    """Simple test route to verify backend is working."""
    return jsonify({
        "message": "Backend is working with Google Vision API", 
        "is_monitoring": is_monitoring,
        "vision_api_ready": vision_client is not None,
        "timestamp": time.time()
    })

@app.route('/api/start', methods=['POST'])
def start_monitoring():
    """Start the monitoring process."""
    global is_monitoring, student_phone, recent_notifications, last_movement_check, previous_detections
    
    print("START ROUTE CALLED!")
    
    if not vision_client:
        return jsonify({"success": False, "message": "Vision API not available"}), 500
    
    try:
        data = request.get_json()
        if data is None:
            return jsonify({"success": False, "message": "No data received"}), 400
        
        phone = data.get('phone')
        if not phone or not phone.strip():
            return jsonify({"success": False, "message": "Phone number is required"}), 400
        
        # Format phone number
        phone = phone.strip()
        if not phone.startswith('+'):
            phone = '+' + phone
        
        # Set global state
        student_phone = phone
        is_monitoring = True
        recent_notifications = []
        last_movement_check = 0
        previous_detections = []  # Reset baseline
        
        print(f"MONITORING ACTIVATED! Phone: {student_phone}")
        return jsonify({"success": True, "message": "Monitoring started successfully"})
        
    except Exception as e:
        print(f"ERROR in start_monitoring: {e}")
        return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500

@app.route('/api/stop', methods=['POST'])
def stop_monitoring():
    """Stop the monitoring process."""
    global is_monitoring, student_phone, recent_notifications, previous_detections
    
    print("Stopping monitoring...")
    is_monitoring = False
    student_phone = None
    recent_notifications = []
    previous_detections = []
    
    return jsonify({"success": True, "message": "Monitoring stopped successfully"})

@app.route('/api/process-frame', methods=['POST'])
def process_frame():
    """Process frames using Google Vision API."""
    global is_monitoring, student_phone, recent_notifications, last_movement_check
    
    if not is_monitoring or not student_phone:
        return jsonify({"error": "Monitoring not active"}), 400
    
    if not vision_client:
        return jsonify({"error": "Vision API not available"}), 500
    
    try:
        # Get uploaded frame
        if 'frame' not in request.files:
            return jsonify({"error": "No frame received"}), 400
        
        frame_file = request.files['frame']
        frame_bytes = frame_file.read()
        
        print(f"Processing frame: {len(frame_bytes)} bytes")
        
        # Detect objects using Google Vision API
        detections = detect_objects_google(frame_bytes)
        detected_labels = [d['label'] for d in detections]
        print(f"Google Vision detected: {detected_labels}")
        
        # Calculate movements (disappearances)
        movements = calculate_movement(detections)
        
        current_time = time.time()
        
        # Send notifications for disappeared objects
        if movements and student_phone and (current_time - last_movement_check > 10.0):
            print(f"DISAPPEARANCES DETECTED: {movements}")
            
            for obj, action in movements.items():
                if action == "disappeared":
                    message = f"SECURITY ALERT: Your {obj} has disappeared! Please check your belongings immediately."
                    
                    try:
                        # Only send SMS if no recent notifications
                        if len(recent_notifications) == 0:
                            notification_result = notifier.send_notification(student_phone, message)
                            if notification_result and len(notification_result) == 2:
                                success_result, result = notification_result
                            else:
                                success_result, result = True, "notification_sent"
                            print(f"SMS sent for {obj}")
                        else:
                            success_result, result = True, "SMS skipped - recent notification exists"
                            print(f"SMS skipped for {obj}")
                        
                        # Store notification
                        recent_notifications.append({
                            "timestamp": current_time,
                            "message": message,
                            "success": success_result,
                            "object": obj,
                            "action": action
                        })
                        
                        # Keep only recent notifications
                        if len(recent_notifications) > 5:
                            recent_notifications.pop(0)
                            
                    except Exception as e:
                        print(f"ERROR in notification: {e}")
            
            last_movement_check = current_time
        
        return jsonify({
            "success": True,
            "detections": detected_labels,
            "movements_detected": movements,
            "timestamp": current_time
        })
        
    except Exception as e:
        print(f"Frame processing error: {e}")
        return jsonify({"error": f"Processing failed: {str(e)}"}), 500

@app.route('/api/check_notifications')
def check_notifications():
    """Return recent notifications."""
    current_time = time.time()
    recent = [n for n in recent_notifications if current_time - n["timestamp"] < 60]
    
    return jsonify({"notifications": recent})

if __name__ == '__main__':
    print("Starting Flask application with Google Vision API...")
    if vision_client:
        print("✅ Google Vision API initialized successfully")
    else:
        print("❌ Google Vision API failed to initialize")
        print("Make sure GOOGLE_APPLICATION_CREDENTIALS is set or GOOGLE_APPLICATION_CREDENTIALS_JSON for cloud!")
    print("Backend API: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)