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


    

