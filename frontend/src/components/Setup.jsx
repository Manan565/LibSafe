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
return (
    <div className="p-8">
      <h2 className="text-2xl font-bold text-blue-900 mb-4 text-center">
        Get Started
      </h2>
      <p className="text-gray-600 text-center mb-6">
        Enter your phone number to receive alerts when your belongings move
      </p>

      <form onSubmit={handleStart} className="max-w-md mx-auto">
        <div className="mb-6">
          <label
            htmlFor="phoneNumber"
            className="block text-gray-700 font-medium mb-2"
          >
            Phone Number:
          </label>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <FaPhoneAlt className="text-gray-400" />
            </div>
            <input
              type="tel"
              id="phoneNumber"
              placeholder="+1234567890"
              value={phoneNumber}
              onChange={(e) => setPhoneNumber(e.target.value)}
              className="pl-10 block w-full rounded-md border border-gray-300 py-3 px-4 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              required
            />
          </div>
          <p className="mt-2 text-sm text-gray-500 flex items-center">
            <FaInfoCircle className="mr-1" /> Include country code (e.g., +1 for
            US)
          </p>
        </div>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

