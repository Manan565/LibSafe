import React from "react";
import { FaShieldAlt } from "react-icons/fa";

const Header = () => {
  return (
    <header className="bg-blue-900 text-white py-6">
      <div className="container mx-auto px-4 max-w-5xl">
        <div className="flex items-center justify-center">
          <FaShieldAlt className="text-4xl mr-3" />
          <div>
            <h1 className="text-3xl font-bold">Library Safety System</h1>
            <p className="text-blue-200">
              Protect your belongings while you're away
            </p>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
