import React, { useState } from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import HomePage from "./HomePage";
import VideoDisplayPage from "./VideoDisplayPage";

function App() {
  const [isUploading, setIsUploading] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [videoData, setVideoData] = useState(null);

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
            />
          }
        />
        <Route
          path="/video"
          element={
            <VideoDisplayPage
              videoData={videoData}
              isUploading={isUploading}
              isProcessing={isProcessing}
              setIsProcessing={setIsProcessing}
            />
          }
        />
      </Routes>
    </Router>
  );
}

export default App;
