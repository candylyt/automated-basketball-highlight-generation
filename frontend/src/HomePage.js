import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import VideoUpload from "./components/VideoUpload";
import "./HomePage.css";

function Home({ setIsUploading, setIsProcessing }) {
  const navigate = useNavigate();
  const [file, setFile] = useState(null);

  useEffect(() => {
    if (file) {
      navigate("/video", { state: { file } });
    }
  }, [file, navigate]);

  return (
    <div className="HomePage">
      <div className="HomePage-header">Basketball Highlights Generation</div>
      <div className="HomePage-description">
        Automatically and efficiently generate scoring highlights and shooting
        statistics with precision
      </div>
      <VideoUpload
        setFile={setFile}
        setIsUploading={setIsUploading}
        setIsProcessing={setIsProcessing}
      />
    </div>
  );
}

export default Home;
