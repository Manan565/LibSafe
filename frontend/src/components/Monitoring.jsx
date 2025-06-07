import React, { useState, useEffect } from "react";
import axios from "axios";
import {
  FaLaptop,
  FaBookOpen,
  FaMobileAlt,
  FaTshirt,
  FaStop,
  FaUmbrellaBeach,
} from "react-icons/fa";

import { GiWaterBottle } from "react-icons/gi";

const Monitoring = ({ phoneNumber, stopMonitoring }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [streamUrl, setStreamUrl] = useState("");

  useEffect(() => {
    console.log("🎬 Monitoring component mounted with phone:", phoneNumber);

    // Start video feed after delay
    setTimeout(() => {
      const timestamp = new Date().getTime();
      console.log("🎥 Starting video feed with timestamp:", timestamp);
      setStreamUrl(`/api/video_feed?t=${timestamp}`);
    }, 3000);

    // IMPORTANT: Only cleanup when component actually unmounts
    //return () => {
    // console.log("🧹 Monitoring component unmounting - calling cleanup");
    //handleStop(false);
    //};
  }, []); // Make sure this is empty dependency array

  const handleStop = async (updateUI = true) => {
    setIsLoading(true);

    try {
      await axios.post("/api/stop");
      if (updateUI) {
        console.log("stopped monitoring");
        stopMonitoring();
      }
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
      <div className="md:w-2/3">
        <div className="video-container">
          {streamUrl ? (
            <img
              src={streamUrl}
              alt="Video feed"
              onError={(e) => {
                console.log("Error loading video feed");
                // Retry with a new timestamp after 2 seconds
                setTimeout(() => {
                  setStreamUrl(`/api/video_feed?t=${new Date().getTime()}`);
                }, 2000);
              }}
            />
          ) : (
            <div className="flex items-center justify-center h-full">
              <p className="text-white text-lg">Connecting to camera...</p>
            </div>
          )}

          <div className="alert-badge">Monitoring Active</div>
        </div>
      </div>

      <div className="md:w-1/3 bg-gray-50 p-6">
        <h2 className="text-2xl font-bold text-blue-900 mb-4">
          Monitoring Active
        </h2>

        <div className="mb-6">
          <p className="text-gray-700 mb-2 font-medium">
            Notifications will be sent to:
          </p>
          <div className="bg-white p-3 rounded border border-gray-200 text-gray-800">
            {phoneNumber}
          </div>
        </div>

        <div className="mb-6">
          <p className="text-gray-700 mb-2 font-medium">
            Watching for movement of:
          </p>
          <ul className="grid grid-cols-2 gap-2">
            {objectList.map((object, index) => (
              <li
                key={index}
                className="flex items-center bg-white p-2 rounded border border-gray-200"
              >
                <span className="text-blue-900 mr-2">{object.icon}</span>
                <span className="text-gray-800">{object.name}</span>
              </li>
            ))}
          </ul>
        </div>

