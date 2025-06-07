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

  