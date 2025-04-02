import React, { useEffect, useState } from "react";
import { useLocation, Link } from "react-router-dom";
import io from "socket.io-client";
import Header from "./components/Header";
import Modal from "react-modal";
import "./VideoDisplayPage.css";
import Statistics from "./components/Statistics";
import {
  convertTimestampToSeconds,
  convertTimestamp,
} from "./components/utils";

Modal.setAppElement("#root");

function VideoDisplayPage({
  videoData,
  isUploading,
  isProcessing,
  setIsProcessing,
}) {
  const location = useLocation();
  const { file1, file2 } = location.state || {};
  console.log("File 1:", file1);
  console.log("File 2:", file2);

  const [selectedAngle, setSelectedAngle] = useState(1);

  // Team A Data
  const [scoringTimestampsA, setScoringTimestampsA] = useState([]);
  const [shootingTimestampsA, setShootingTimestampsA] = useState([]);
  const [makesA, setMakesA] = useState([]);
  const [attemptsA, setAttemptsA] = useState([]);

  // Team B Data
  const [scoringTimestampsB, setScoringTimestampsB] = useState([]);
  const [shootingTimestampsB, setShootingTimestampsB] = useState([]);
  const [makesB, setMakesB] = useState([]);
  const [attemptsB, setAttemptsB] = useState([]);

  const [isConnected, setIsConnected] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleTimestampClick = (timestamp) => {
    const seconds = convertTimestampToSeconds(timestamp);
    const video = document.querySelector("video");
    video.currentTime = seconds;
    video.play();
    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  };

  const handleReturnHome = () => {
    window.location.href = "/";
  };

  const backendPort = process.env.REACT_APP_BACKEND_PORT;

  useEffect(() => {
    // Connect to the WebSocket server
    const socket = io(backendPort);

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
      // processing == false after the first shooting_detected event
      setIsProcessing(false);
      console.log("Shooting detected:", data);

      // const timestamp = convertMillisecondsToTimestamp(data.start_time);
      const timestamp = convertTimestamp(data.start_time);

      // Scoring Moments
      if (data.success) {
        // Add the timestamp to Team A
        if (data.team === "A" || !data.team) {
          setScoringTimestampsA((prevTimestamps) => {
            if (!prevTimestamps.includes(timestamp)) {
              return [...prevTimestamps, timestamp];
            }
            return prevTimestamps;
          });
        } else {
          // Add the timestamp to Team B
          setScoringTimestampsB((prevTimestamps) => {
            if (!prevTimestamps.includes(timestamp)) {
              return [...prevTimestamps, timestamp];
            }
            return prevTimestamps;
          });
        }
      }
      // Shooting Moments
      else {
        // Add the timestamp to Team A
        if (data.team === "A" || !data.team) {
          setShootingTimestampsA((prevTimestamps) => {
            if (!prevTimestamps.includes(timestamp)) {
              return [...prevTimestamps, timestamp];
            }
            return prevTimestamps;
          });
        } else {
          // Add the timestamp to Team B
          setShootingTimestampsB((prevTimestamps) => {
            if (!prevTimestamps.includes(timestamp)) {
              return [...prevTimestamps, timestamp];
            }
            return prevTimestamps;
          });
        }
      }
    });

    // Listen for the 'processing_complete' event
    socket.on("processing_complete", (data) => {
      console.log("Processing complete:", data);
      setIsProcessing(false);

      if (data.is_match) {
        setMakesA(data.team_A_makes);
        setAttemptsA(data.team_A_attempts);
        setMakesB(data.team_B_makes);
        setAttemptsB(data.team_B_attempts);
      } else {
        setMakesA(data.makes);
        setAttemptsA(data.attempts);
      }
      setIsModalOpen(true);
      socket.disconnect();
    });

    // Handle connection errors
    socket.on("connect_error", (error) => {
      console.error("Connection error:", error);
    });
  }, []);

  const closeModal = () => {
    setIsModalOpen(false);
  };

  return (
    <div className="VD-background">
      <Header />
      {file1 ? (
        <div className="VD-container">
          <div className="VD-videoContainer">
            {file2 && (
              <div className="VD-cameraSelection">
                <div
                  className={
                    selectedAngle === 1
                      ? "VD-cameraAngleSelected"
                      : "VD-cameraAngle"
                  }
                  onClick={() => setSelectedAngle(1)}
                >
                  Camera Angle 1
                </div>
                <div
                  className={
                    selectedAngle === 2
                      ? "VD-cameraAngleSelected"
                      : "VD-cameraAngle"
                  }
                  onClick={() => setSelectedAngle(2)}
                >
                  Camera Angle 2
                </div>
              </div>
            )}
            {selectedAngle === 1 && (
              <video controls>
                <source src={URL.createObjectURL(file1)} type={file1.type} />
              </video>
            )}
            {selectedAngle === 2 && (
              <video controls>
                <source src={URL.createObjectURL(file2)} type={file2.type} />
              </video>
            )}
            <div className="VD-timestamps">
              <div
                className={
                  videoData.isMatch
                    ? "VD-timestampsTeam"
                    : "VD-timestampsNoTeam"
                }
              >
                {videoData.isMatch && (
                  <div className="VD-timestampTeamTitle">Team A</div>
                )}
                <div className="VD-timestampTitle">
                  Scoring Moment Timestamps
                </div>
                <div className="VD-timestampsContainer">
                  {scoringTimestampsA.map((timestamp, index) => (
                    <div
                      key={index}
                      className="VD-scoringTimestamp"
                      onClick={() => {
                        handleTimestampClick(timestamp);
                      }}
                    >
                      {timestamp}
                    </div>
                  ))}
                </div>
                <div className="VD-timestampTitle">
                  Shooting Moment Timestamps
                </div>
                <div className="VD-timestampsContainer">
                  {shootingTimestampsA.map((timestamp, index) => (
                    <div
                      key={index}
                      className="VD-shootingTimestamp"
                      onClick={() => {
                        handleTimestampClick(timestamp);
                      }}
                    >
                      {timestamp}
                    </div>
                  ))}
                </div>
              </div>
              {videoData.isMatch && (
                <div className="VD-timestampsTeam">
                  <div className="VD-timestampTeamTitle">Team B</div>

                  <div className="VD-timestampTitle">
                    Scoring Moment Timestamps
                  </div>
                  <div className="VD-timestampsContainer">
                    {scoringTimestampsB.map((timestamp, index) => (
                      <div
                        key={index}
                        className="VD-scoringTimestamp"
                        onClick={() => {
                          handleTimestampClick(timestamp);
                        }}
                      >
                        {timestamp}
                      </div>
                    ))}
                  </div>
                  <div className="VD-timestampTitle">
                    Shooting Moment Timestamps
                  </div>
                  <div className="VD-timestampsContainer">
                    {shootingTimestampsB.map((timestamp, index) => (
                      <div
                        key={index}
                        className="VD-shootingTimestamp"
                        onClick={() => {
                          handleTimestampClick(timestamp);
                        }}
                      >
                        {timestamp}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {isUploading && (
              <div className="VD-loading">
                <div className="VD-overlay" />
                <div className="VD-uploading">
                  Uploading Video &nbsp;
                  <div className="VD-spinner" />
                </div>
              </div>
            )}
            {isProcessing && (
              <div className="VD-loading">
                <div className="VD-overlay" />
                <div className="VD-uploading">
                  Processing Video &nbsp;
                  <div className="VD-spinner-square" />
                </div>
              </div>
            )}
          </div>
          <Statistics
            data={{ makesA, makesB, attemptsA, attemptsB }}
            videoData={videoData}
            timestamps={{
              scoringTimestampsA,
              scoringTimestampsB,
              shootingTimestampsA,
              shootingTimestampsB,
            }}
            video={file1}
          />
          <Modal
            isOpen={isModalOpen}
            onRequestClose={closeModal}
            contentLabel="Processing Complete"
            className="VD-modal"
          >
            <div className="VD-modalContent">
              <h2>Processing Complete</h2>
              <p>
                All scoring and shooting moments have been identified. You can
                now export the highlight videos and statistics.
              </p>
              <button onClick={closeModal}>Close</button>
            </div>
          </Modal>
        </div>
      ) : (
        <div className="VD-error">
          Error: No video file has been uploaded. Return to &nbsp;
          <div className="VD-hpButton" onClick={handleReturnHome}>
            Home Page
          </div>
          .
        </div>
      )}
    </div>
  );
}

export default VideoDisplayPage;
