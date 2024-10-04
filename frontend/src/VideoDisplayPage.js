import React, { useEffect } from "react";
import { useLocation, Link } from "react-router-dom";
import Header from "./components/Header";
import "./VideoDisplayPage.css";
import Statistics from "./components/Statistics";

function VideoDisplayPage() {
  const location = useLocation();
  const { file } = location.state || {};

  const timestamps = ["1:26", "3:12", "7:02"];

  const convertTimestampToSeconds = (timestamp) => {
    const [minutes, seconds] = timestamp.split(":");
    return parseInt(minutes) * 60 + parseInt(seconds);
  };

  const handleTimestampClick = (timestamp) => {
    const seconds = convertTimestampToSeconds(timestamp);
    const video = document.querySelector("video");
    video.currentTime = seconds;
    video.play();
  };

  return (
    <div className="VD-background">
      <Header />
      {file ? (
        <div className="VD-container">
          <div className="VD-videoContainer">
            <video controls>
              <source src={URL.createObjectURL(file)} type={file.type} />
            </video>
            <div className="VD-timestampTitle">Scoring Moment Timestamps</div>
            <div className="VD-timestampsContainer">
              {timestamps.map((timestamp, index) => (
                <div
                  key={index}
                  className="VD-timestamp"
                  onClick={() => {
                    handleTimestampClick(timestamp);
                  }}
                >
                  {timestamp}
                </div>
              ))}
            </div>
          </div>
          <Statistics />
        </div>
      ) : (
        <div className="VD-error">
          Error: No video file has been uploaded. Return to &nbsp;
          <Link to="/">Home Page</Link>.
        </div>
      )}
    </div>
  );
}

export default VideoDisplayPage;
