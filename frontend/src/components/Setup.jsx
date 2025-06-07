import React, { useState } from "react";
import axios from "axios";
import { FaPhoneAlt, FaPlay, FaInfoCircle } from "react-icons/fa";

const Setup = ({ phoneNumber, setPhoneNumber, startMonitoring }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const handleStart = async (e) => {
    e.preventDefault();

    console.log("🎯 handleStart called with phone:", phoneNumber);

    if (!phoneNumber) {
      setError("Please enter your phone number to receive alerts");
      return;
    }

    setIsLoading(true);
    setError("");

    try {
      console.log("📤 Making request to /api/start with:", {
        phone: phoneNumber,
      });

      const response = await axios.post("http://localhost:5000/api/start", {
        phone: phoneNumber,
      });

      console.log("📥 Response received:", response.data);

      if (response.data.success) {
        console.log("✅ Success! Calling startMonitoring()");

        // Add a small delay to ensure backend state is set
        setTimeout(() => {
          startMonitoring();
        }, 500);
      } else {
        setError(response.data.message || "Something went wrong");
      }
    } catch (err) {
      console.error("❌ Error starting monitoring:", err);
      console.error("❌ Error details:", err.response);
      setError(err.response?.data?.message || "Failed to start monitoring");
    } finally {
      setIsLoading(false);
    }
  };
