import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import VideoUpload from "./components/VideoUpload";
import "./HomePage.css";

function Home({ videoData, setVideoData, setIsUploading, setIsProcessing }) {
  const navigate = useNavigate();
  const [file1, setFile1] = useState(null);
  const [file2, setFile2] = useState(null);
  // const [videoData, setVideoData] = useState(null);

  useEffect(() => {
    if (videoData) {
      navigate("/video", { state: { file1 } });
    }
  }, [videoData, navigate]);

  return (
    <div className="HomePage">
      <div className="HomePage-header">Basketball Highlights Generation</div>
      <div className="HomePage-description">
        Automatically and efficiently generate scoring highlights and shooting
        statistics with precision
      </div>
      <VideoUpload
        file1={file1}
        file2={file2}
        setFile1={setFile1}
        setFile2={setFile2}
        setIsUploading={setIsUploading}
        setIsProcessing={setIsProcessing}
        setVideoData={setVideoData}
      />
    </div>
  );
}

export default Home;
