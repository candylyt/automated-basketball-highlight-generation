import React from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import HomePage from "./HomePage";
import VideoDisplayPage from "./VideoDisplayPage";

function App() {
  return (
    <Router>
      <Routes>
        <Route exact path="/" element={<HomePage />} />
        <Route path="/video" element={<VideoDisplayPage />} />
      </Routes>
    </Router>
  );
}

export default App;
