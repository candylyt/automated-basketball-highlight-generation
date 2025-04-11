import React, { useState } from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import HomePage from "./HomePage";
import VideoDisplayPage from "./VideoDisplayPage";

function App() {
  const [isUploading, setIsUploading] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [videoData, setVideoData] = useState(null);
  const [runId, setRunId] = useState(null);

  return (
    <Router>
      <Routes>
        <Route
          exact
          path="/"
          element={
            <HomePage
              videoData={videoData}
              setVideoData={setVideoData}
              setIsUploading={setIsUploading}
              setIsProcessing={setIsProcessing}
              setRunId={setRunId}
            />
          }
        />
        <Route
          path="/video"
          element={
            <VideoDisplayPage
              runId={runId}
              videoData={videoData}
              isUploading={isUploading}
              isProcessing={isProcessing}
              setIsProcessing={setIsProcessing}
            />
          }
        />
        <Route path="/export" />
      </Routes>
    </Router>
  );
}

export default App;
