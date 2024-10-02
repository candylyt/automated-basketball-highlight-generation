import React from "react";
import VideoUpload from "./components/VideoUpload";
import "./HomePage.css";

function Home() {
  return (
    <div className="Home">
      <header className="Home-header">Basketball Highlights Generation</header>
      <div className="Home-description">
        Automatically and efficiently generate scoring highlights and shooting
        statistics with precision
      </div>
      <VideoUpload />
    </div>
  );
}

export default Home;
