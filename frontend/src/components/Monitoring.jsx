import React, { useState, useRef, useEffect } from "react";
import axios from "axios";
import {
  FaLaptop,
  FaBookOpen,
  FaMobileAlt,
  FaTshirt,
  FaStop,
  FaUmbrellaBeach,
  FaCamera,
  FaExclamationTriangle
} from "react-icons/fa";
import { GiWaterBottle } from "react-icons/gi";

const Monitoring = ({ phoneNumber, stopMonitoring }) => {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [notifications, setNotifications] = useState([]);
  const [processedFrame, setProcessedFrame] = useState(null);
  const intervalRef = useRef(null);
  const notificationIntervalRef = useRef(null);

  useEffect(() => {
    console.log("Monitoring component mounted with phone:", phoneNumber);
    startCamera();
    
    // Check for notifications every 3 seconds
    
    return () => {
      console.log("Monitoring component unmounting - cleaning up");
      stopCamera();
      if (notificationIntervalRef.current) {
        clearInterval(notificationIntervalRef.current);
      }
    };
  }, []);

  const startCamera = async () => {
  try {
    console.log("Requesting camera access...");
    
    const stream = await navigator.mediaDevices.getUserMedia({ 
      video: { 
        width: { ideal: 1280 }, 
        height: { ideal: 720 },
        facingMode: 'user'
      } 
    });
    
    if (videoRef.current) {
      videoRef.current.srcObject = stream;
      
      // Set streaming state immediately after stream assignment
      setIsStreaming(true);
      setError('');
      console.log("Camera stream assigned, isStreaming set to true");
      
      // Start interval after longer delay to ensure video is ready
      setTimeout(() => {
        console.log("Starting capture interval");
        intervalRef.current = setInterval(captureAndSend, 3000);
      }, 5000); // Increased from 2000 to 5000
    }
  } catch (err) {
    console.error("Error accessing camera:", err);
    setError(`Camera access failed: ${err.message}`);
  }
};

  const stopCamera = () => {
    console.log("Stopping camera...");
    
    if (videoRef.current && videoRef.current.srcObject) {
      const tracks = videoRef.current.srcObject.getTracks();
      tracks.forEach(track => track.stop());
      videoRef.current.srcObject = null;
    }
    
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    
    setIsStreaming(false);
  };

  const captureAndSend = async () => {
  console.log('captureAndSend called');
  console.log('videoRef.current:', !!videoRef.current);
  console.log('canvasRef.current:', !!canvasRef.current);
  
  if (!videoRef.current || !canvasRef.current) {
    console.log("Cannot capture - refs not available");
    return;
  }

  const video = videoRef.current;
  
  // Check video readiness instead of isStreaming state
  if (video.readyState < 2) {
    console.log("Video not ready, readyState:", video.readyState);
    return;
  }

  if (video.videoWidth === 0 || video.videoHeight === 0) {
    console.log("Video dimensions not available");
    return;
  }

  console.log(`Video ready: ${video.videoWidth}x${video.videoHeight}, readyState: ${video.readyState}`);

  try {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    console.log(`Capturing frame: ${canvas.width}x${canvas.height}`);

    canvas.toBlob(async (blob) => {
      if (!blob) {
        console.log("Failed to create blob from canvas");
        return;
      }

      const formData = new FormData();
      formData.append('frame', blob, 'frame.jpg');

      try {
        console.log("Sending frame to backend...");
        const response = await axios.post(' http://localhost:5000/api/process-frame', formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
          timeout: 10000
        });

        console.log("Frame processing response:", response.data);

      } catch (err) {
        console.error("Error sending frame:", err);
      }
    }, 'image/jpeg', 0.95);

  } catch (err) {
    console.error("Error in captureAndSend:", err);
  }
};

  const checkNotifications = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/check_notifications');
      if (response.data.notifications && response.data.notifications.length > 0) {
        setNotifications(response.data.notifications);
        console.log("Updated notifications:", response.data.notifications.length);
      }
    } catch (err) {
      console.error("Error checking notifications:", err);
    }
  };

  const handleStop = async () => {
    setIsLoading(true);
    
    try {
      console.log("Stopping monitoring...");
      await axios.post('http://localhost:5000/api/stop');
      stopCamera();
      console.log("Monitoring stopped successfully");
      stopMonitoring();
    } catch (err) {
      console.error("Error stopping monitoring:", err);
      setError("Failed to stop monitoring. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const objectList = [
    { name: "Laptop", icon: <FaLaptop /> },
    { name: "Books", icon: <FaBookOpen /> },
    { name: "Cell Phone", icon: <FaMobileAlt /> },
    { name: "Backpack", icon: <FaTshirt /> },
    { name: "Bottle", icon: <GiWaterBottle /> },
    { name: "Umbrella", icon: <FaUmbrellaBeach /> },
  ];

  return (
    <div className="flex flex-col md:flex-row">
      <div className="md:w-2/3 p-4">
        <div className="relative bg-black rounded-lg overflow-hidden">
          {/* Live Video Feed */}
          <video
            ref={videoRef}
            autoPlay
            muted
            playsInline
            className="w-full h-auto max-h-96 object-cover"
          />
          
          {/* Processed Frame Overlay (Optional) */}
          {processedFrame && (
            <img
              src={processedFrame}
              alt="Processed frame"
              className="absolute top-0 left-0 w-full h-full object-cover opacity-50"
            />
          )}
          
          {isStreaming && (
            <div className="absolute top-4 left-4 bg-red-600 text-white px-3 py-1 rounded-full text-sm flex items-center">
              <div className="w-2 h-2 bg-white rounded-full mr-2 animate-pulse"></div>
              LIVE MONITORING
            </div>
          )}
          
          {error && (
            <div className="absolute bottom-4 left-4 right-4 bg-red-900 bg-opacity-90 text-white p-3 rounded">
              <div className="flex items-center">
                <FaExclamationTriangle className="mr-2" />
                <span className="text-sm">{error}</span>
              </div>
            </div>
          )}
        </div>

        {/* Hidden canvas for frame capture */}
        <canvas ref={canvasRef} style={{ display: 'none' }} />
      </div>

      <div className="md:w-1/3 bg-gray-50 p-6">
        <h2 className="text-2xl font-bold text-blue-900 mb-4">
          Live Monitoring
        </h2>

        <div className="mb-6">
          <p className="text-gray-700 mb-2 font-medium">
            Notifications sent to:
          </p>
          <div className="bg-white p-3 rounded border border-gray-200">
            {phoneNumber}
          </div>
        </div>

        {notifications.length > 0 && (
          <div className="mb-6">
            <p className="text-gray-700 mb-2 font-medium">Recent Alerts:</p>
            <div className="space-y-2 max-h-40 overflow-y-auto">
              {notifications.slice(-5).reverse().map((notif, index) => (
                <div key={index} className="bg-yellow-100 border border-yellow-300 text-yellow-800 px-3 py-2 rounded text-sm">
                  <div className="font-medium">{notif.message}</div>
                  <div className="text-xs opacity-75">
                    {new Date(notif.timestamp * 1000).toLocaleTimeString()}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="mb-6">
          <p className="text-gray-700 mb-2 font-medium">Watching for movement of:</p>
          <ul className="grid grid-cols-2 gap-2">
            {objectList.map((object, index) => (
              <li
                key={index}
                className="flex items-center bg-white p-2 rounded border border-gray-200"
              >
                <span className="text-blue-900 mr-2">{object.icon}</span>
                <span className="text-gray-800 text-sm">{object.name}</span>
              </li>
            ))}
          </ul>
        </div>

        <div className="mb-6">
          <p className="text-gray-700 mb-2 font-medium">Status:</p>
          <div className="bg-white p-3 rounded border border-gray-200">
            {isStreaming ? (
              <span className="text-green-600 font-medium flex items-center">
                <FaCamera className="mr-2" />
                Camera Active
              </span>
            ) : (
              <span className="text-red-600 font-medium flex items-center">
                <FaExclamationTriangle className="mr-2" />
                Camera Inactive
              </span>
            )}
          </div>
        </div>

        <p className="text-gray-600 mb-6 text-sm">
          Your camera captures frames every 3 seconds and processes them for object detection. 
          If any items move or disappear, you'll receive an SMS alert.
        </p>

        <button
          onClick={handleStop}
          disabled={isLoading}
          className="w-full bg-red-600 text-white py-3 px-4 rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 flex items-center justify-center disabled:bg-red-300"
        >
          {isLoading ? (
            <>
              <span className="animate-spin mr-2">⟳</span>
              Stopping...
            </>
          ) : (
            <>
              <FaStop className="mr-2" />
              Stop Monitoring
            </>
          )}
        </button>
      </div>
    </div>
  );
};

export default Monitoring;