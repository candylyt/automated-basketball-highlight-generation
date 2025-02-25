import React, { useState } from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import HomePage from "./HomePage";
import VideoDisplayPage from "./VideoDisplayPage";

function App() {
  const [isUploading, setIsUploading] = useState(true);
  const [isProcessing, setIsProcessing] = useState(false);
  return (
    <Router>
      <Routes>
        <Route
          exact
          path="/"
          element={
            <HomePage
              setIsUploading={setIsUploading}
              setIsProcessing={setIsProcessing}
            />
          }
        />
        <Route
          path="/video"
          element={
            <VideoDisplayPage
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
