import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import {
  FaLaptop,
  FaBookOpen,
  FaMobileAlt,
  FaTshirt,
  FaStop,
  FaUmbrellaBeach,
  FaCamera,
  FaExclamationTriangle
} from 'react-icons/fa';
import { GiWaterBottle } from 'react-icons/gi';

const Monitoring = ({ phoneNumber, stopMonitoring }) => {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [notifications, setNotifications] = useState([]);
  const [cameraSupported, setCameraSupported] = useState(true);
  const [streamStats, setStreamStats] = useState({ framesSent: 0, lastSent: null });
  const intervalRef = useRef(null);
  const notificationIntervalRef = useRef(null);

  useEffect(() => {
    console.log('🎬 Cloud Monitoring component mounted with phone:', phoneNumber);
    startCamera();
    
    // Check for notifications every 3 seconds
    notificationIntervalRef.current = setInterval(checkNotifications, 3000);
    
    return () => {
      console.log('🧹 Cloud Monitoring component unmounting - cleaning up');
      stopCamera();
      if (notificationIntervalRef.current) {
        clearInterval(notificationIntervalRef.current);
      }
    };
  }, []);

  const startCamera = async () => {
    try {
      console.log('📷 Requesting camera access...');
      // Check if getUserMedia is supported
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        throw new Error('Camera not supported in this browser');
      }

      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { 
          width: { ideal: 640 }, 
          height: { ideal: 480 },
          facingMode: 'user' // Use front camera if available
        } 
      });
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        setIsStreaming(true);
        setError('');
        console.log('✅ Camera started successfully');
        
        // Start sending frames to backend every 3 seconds
        intervalRef.current = setInterval(captureAndSend, 3000);
      }
    } catch (err) {
      console.error('❌ Error accessing camera:', err);
      setCameraSupported(false);
      setError(`Camera access failed: ${err.message}. Please ensure camera permissions are granted.`);
    }
  };

  const stopCamera = () => {
    console.log('🛑 Stopping camera...');
    
    if (videoRef.current && videoRef.current.srcObject) {
      const tracks = videoRef.current.srcObject.getTracks();
      tracks.forEach(track => {
        track.stop();
        console.log('📷 Camera track stopped');
      });
      videoRef.current.srcObject = null;
    }
    
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    
    setIsStreaming(false);
  };

  const captureAndSend = async () => {
    if (!videoRef.current || !canvasRef.current || !isStreaming) {
      console.log('⚠️ Cannot capture - video or canvas not ready');
      return;
    }

    try {
      const canvas = canvasRef.current;
      const video = videoRef.current;
      const ctx = canvas.getContext('2d');

      // Set canvas size to match video
      canvas.width = video.videoWidth || 640;
      canvas.height = video.videoHeight || 480;

      // Draw current video frame to canvas
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

      // Convert canvas to blob
      canvas.toBlob(async (blob) => {
        if (!blob) {
          console.log('❌ Failed to create blob from canvas');
          return;
        }

        const formData = new FormData();
        formData.append('frame', blob, 'frame.jpg');
        formData.append('phone', phoneNumber);

        try {
          console.log('📤 Sending frame to backend...');
          const response = await axios.post('/api/process-frame', formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
            timeout: 10000 // 10 second timeout
          });

          console.log('📥 Frame processing response:', response.data);

          if (response.data.movements_detected) {
            console.log('🎯 Movements detected:', response.data.movements_detected);
          }

          // Update stats
          setStreamStats(prev => ({
            framesSent: prev.framesSent + 1,
            lastSent: new Date().toLocaleTimeString()
          }));

        } catch (err) {
          console.error('❌ Error sending frame:', err);
          if (err.response?.status === 400) {
            console.log('⚠️ Monitoring may have been stopped on backend');
          }
        }
      }, 'image/jpeg', 0.8);

    } catch (err) {
      console.error('❌ Error in captureAndSend:', err);
    }
  };

  const checkNotifications = async () => {
    try {
      const response = await axios.get('/api/check_notifications');
      if (response.data.notifications && response.data.notifications.length > 0) {
        setNotifications(response.data.notifications);
        console.log('📋 Updated notifications:', response.data.notifications.length);
      }
    } catch (err) {
      console.error('❌ Error checking notifications:', err);
    }
  };

  const handleStop = async () => {
    setIsLoading(true);
    
    try {
      console.log('🛑 Stopping monitoring...');
      await axios.post('/api/stop');
      stopCamera();
      console.log('✅ Monitoring stopped successfully');
      stopMonitoring();
    } catch (err) {
      console.error('❌ Error stopping monitoring:', err);
      setError('Failed to stop monitoring. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const objectList = [
    { name: 'Laptop', icon: <FaLaptop /> },
    { name: 'Books', icon: <FaBookOpen /> },
    { name: 'Cell Phone', icon: <FaMobileAlt /> },
    { name: 'Backpack', icon: <FaTshirt /> },
    { name: 'Bottle', icon: <GiWaterBottle /> },
    { name: 'Umbrella', icon: <FaUmbrellaBeach /> },
  ];

  return (
    <div className="flex flex-col md:flex-row">
      <div className="md:w-2/3 p-4">
        <div className="relative bg-black rounded-lg overflow-hidden">
          {cameraSupported ? (
            <>
              <video
                ref={videoRef}
                autoPlay
                muted
                playsInline
                className="w-full h-auto max-h-96 object-cover"
              />
              
              {isStreaming && (
                <div className="absolute top-4 left-4 bg-red-600 text-white px-3 py-1 rounded-full text-sm flex items-center">
                  <div className="w-2 h-2 bg-white rounded-full mr-2 animate-pulse"></div>
                  LIVE MONITORING
                </div>
              )}

              {isStreaming && (
                <div className="absolute top-4 right-4 bg-blue-600 text-white px-3 py-1 rounded-full text-xs">
                  Frames: {streamStats.framesSent}
                </div>
              )}
            </>
          ) : (
            <div className="flex flex-col items-center justify-center h-96 text-white p-4">
              <FaExclamationTriangle className="text-4xl mb-4 text-yellow-500" />
              <h3 className="text-xl mb-2">Camera Not Available</h3>
              <p className="text-center text-sm opacity-75">
                This device doesn't support camera access or permissions were denied.
                Please ensure you're using a modern browser with camera support.
              </p>
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

        {/* Stream Info */}
        {isStreaming && (
          <div className="mt-4 p-3 bg-gray-100 rounded-lg">
            <h4 className="font-medium text-gray-700 mb-2">Stream Status</h4>
            <div className="grid grid-cols-2 gap-4 text-sm text-gray-600">
              <div>
                <span className="font-medium">Frames Sent:</span> {streamStats.framesSent}
              </div>
              <div>
                <span className="font-medium">Last Frame:</span> {streamStats.lastSent || 'None'}
              </div>
            </div>
          </div>
        )}
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
                  <div className="font-medium">{notif.object} {notif.action}</div>
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
          Your camera captures frames every 3 seconds and sends them to our server for object detection. 
          If any items move or disappear, you'll receive an SMS alert.
        </p>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4 text-sm">
            {error}
          </div>
        )}

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