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
