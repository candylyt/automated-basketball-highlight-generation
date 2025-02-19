import React, { useEffect, useState } from "react";
import { useLocation, Link } from "react-router-dom";
import io from "socket.io-client";
import Header from "./components/Header";
import "./VideoDisplayPage.css";
import Statistics from "./components/Statistics";

function VideoDisplayPage() {
  const location = useLocation();
  const { file } = location.state || {};

  const [timestamps, setTimestamps] = useState([]);
  const [statistics, setStatistics] = useState(null);
  const [isConnected, setIsConnected] = useState(false);

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

  const convertMillisecondsToTimestamp = (milliseconds) => {
    const totalSeconds = Math.floor(milliseconds / 1000);
    const hours = Math.floor(totalSeconds / 3600);
    const minutes = Math.floor((totalSeconds % 3600) / 60);
    const seconds = totalSeconds % 60;

    const pad = (num) => String(num).padStart(2, "0");
    if (hours > 0) {
      return `${hours}:${pad(minutes)}:${pad(seconds)}`;
    } else {
      return `${minutes}:${pad(seconds)}`;
    }
  };

  const backendPort = process.env.REACT_APP_BACKEND_PORT;

  useEffect(() => {
    const socket = io(backendPort);
    // Connect to the WebSocket server
    console.log("useEffect");

    // Handle connection and disconnection events
    socket.on("connect", () => {
      console.log("Connected to WebSocket server");
      setIsConnected(true);
    });

    socket.on("disconnect", () => {
      console.log("Disconnected from WebSocket server");
      setIsConnected(false);
    });

    // Listen for the 'shooting_detected' event
    socket.on("shooting_detected", (data) => {
      console.log("Shooting detected:", data);

      if (data.success) {
        const timestamp = convertMillisecondsToTimestamp(data.start_time);
        setTimestamps((prevTimestamps) => {
          if (!prevTimestamps.includes(timestamp)) {
            return [...prevTimestamps, timestamp];
          }
          return prevTimestamps;
        });
      }
    });

    // Listen for the 'processing_complete' event
    socket.on("processing_complete", (data) => {
      console.log("Processing complete:", data);
      setStatistics(data);
      socket.disconnect();
    });

    // Handle connection errors
    socket.on("connect_error", (error) => {
      console.error("Connection error:", error);
    });
  }, []);

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
          <Statistics data={statistics} timestamps={timestamps} video={file} />
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
