import React from "react";
import "./Header.css";

const handleReturnHome = () => {
  window.location.href = "/?refresh=true"; // Navigate to home and force reload
};

function Header() {
  return (
    <div>
      <h1 className="Header" onClick={handleReturnHome}>
        Basketball Highlights Generation
      </h1>
    </div>
  );
}

export default Header;
