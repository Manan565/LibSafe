import { useState } from "react";
import Header from "./components/Header";
import Setup from "./components/Setup";
import Monitoring from "./components/Monitoring";
import Footer from "./components/Footer";
import "./index.css";

function App() {
  const [isMonitoring, setIsMonitoring] = useState(false);
  const [phoneNumber, setPhoneNumber] = useState("");

  const startMonitoring = () => {
    console.log(
      "🎯 App.jsx startMonitoring called - switching to monitoring view"
    );
    console.log("📱 Phone number being passed:", phoneNumber);
    setIsMonitoring(true);
  };

  const stopMonitoring = () => {
    console.log("🛑 App.jsx stopMonitoring called - switching to setup view");
    setIsMonitoring(false);
  };

  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-grow container mx-auto p-4 max-w-5xl">
        <div className="bg-white shadow-md rounded-lg overflow-hidden">
          {!isMonitoring ? (
            <Setup
              phoneNumber={phoneNumber}
              setPhoneNumber={setPhoneNumber}
              startMonitoring={startMonitoring}
            />
          ) : (
            <Monitoring
              phoneNumber={phoneNumber}
              stopMonitoring={stopMonitoring}
            />
          )}
        </div>
      </main>
      <Footer />
    </div>
  );
}

export default App;
