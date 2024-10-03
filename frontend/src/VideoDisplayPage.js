import React, { useEffect } from "react";
import { useLocation, Link } from "react-router-dom";
import "./VideoDisplayPage.css";

function VideoDisplayPage() {
  const location = useLocation();
  const { file } = location.state || {};

  return (
    <div className="VD-background">
      <h1>Basketball Highlights Generation</h1>
      {file ? (
        <div className="VD-container">
          <div className="VD-videoContainer">
            <video controls>
              <source src={URL.createObjectURL(file)} type={file.type} />
            </video>
          </div>
          <div className="VD-statistics">
            <h2>Statistics</h2>
            <div className="VD-division" />
          </div>
        </div>
      ) : (
        <div>
          No video file uploaded. Return to <Link to="/">Home Page</Link>.
        </div>
      )}
    </div>
  );
}

export default VideoDisplayPage;
