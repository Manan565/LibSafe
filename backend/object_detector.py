import cv2
import numpy as np
import time
from datetime import datetime

class ObjectDetector:
    def __init__(self, confidence_threshold=0.5, sensitivity=50.0):
        self.confidence_threshold = confidence_threshold
        self.sensitivity = sensitivity
        self.prev_detections = []
        self.class_names = []
        self.net = None
        self.output_layers = None
        self.last_notification_time = {}  # To prevent notification spam
        self.setup_model()

    def setup_model(self):
      """Load YOLOv4 model and class names."""
      print("Loading YOLO model...")
      
      # Load COCO class names
      with open('coco.names', 'r') as f:
          self.class_names = f.read().strip().split('\n')
          
      # Load YOLOv4 model
      self.net = cv2.dnn.readNetFromDarknet('yolov4.cfg', 'yolov4.weights')
      
      # Force OpenCV to use DirectShow on Windows
      # (this often works better than the default Media Foundation backend)
      self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
      self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
      
      # Get output layer names
      layer_names = self.net.getLayerNames()
      self.output_layers = [layer_names[i - 1] for i in self.net.getUnconnectedOutLayers()]
      
      print("Model loaded successfully!")

    def detect_objects(self, frame, target_objects):
        """Detect objects in a frame."""
        height, width, _ = frame.shape
        
        # Create blob from image
        blob = cv2.dnn.blobFromImage(frame, 1/255.0, (416, 416), swapRB=True, crop=False)
        
        # Set input to the network
        self.net.setInput(blob)
        
        # Run forward pass
        outputs = self.net.forward(self.output_layers)
        
        # Process outputs
        class_ids = []
        confidences = []
        boxes = []

        for output in outputs:
            for detection in output:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                
                if confidence > self.confidence_threshold and self.class_names[class_id] in target_objects:
                    # Object detected
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)
                    
                    # Rectangle coordinates
                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)
                    
                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)
        # Apply non-max suppression to remove redundant overlapping boxes
        indices = cv2.dnn.NMSBoxes(boxes, confidences, self.confidence_threshold, 0.4)
        
        # Create detections list with class, box, and confidence
        detections = []
        if len(indices) > 0:
            for i in indices.flatten():
                label = self.class_names[class_ids[i]]
                if label in target_objects:
                    x, y, w, h = boxes[i]
                    detections.append({
                        'label': label,
                        'box': [x, y, w, h],
                        'confidence': confidences[i],
                        'center': [x + w//2, y + h//2]  # Center point for movement tracking
                    })
                    
        return detections
    def calculate_movement(self, current_detections, target_objects):
        """Calculate movement between previous and current detections."""
        # If no previous detections, can't calculate movement
        if not self.prev_detections:
            self.prev_detections = current_detections
            return {}
        
        movements = {}
        
        # Create dictionaries for easier lookup
        prev_dict = {d['label']: d for d in self.prev_detections}
        curr_dict = {d['label']: d for d in current_detections}
        
        # Check each object type we're tracking
        for label in target_objects:
            current_time = time.time()

             
            # Skip objects that received a notification in the last 30 seconds
            if label in self.last_notification_time and current_time - self.last_notification_time[label] < 30:
                continue
                
            # If object disappeared
            if label in prev_dict and label not in curr_dict:
                movements[label] = "disappeared"
                self.last_notification_time[label] = current_time
                continue
                
            # If object still exists, check distance moved
            if label in prev_dict and label in curr_dict:
                prev_center = prev_dict[label]['center']
                curr_center = curr_dict[label]['center']
                
                # Calculate Euclidean distance
                distance = np.sqrt((prev_center[0] - curr_center[0])**2 + 
                                  (prev_center[1] - curr_center[1])**2)
                
                # If distance greater than sensitivity threshold, consider it moved
                if distance > self.sensitivity:
                    movements[label] = "moved"
                    self.last_notification_time[label] = current_time
        
        # Update previous detections
        self.prev_detections = current_detections
        
        return movements

    



    

