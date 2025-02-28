import React, { useState } from "react";
import { ReactComponent as VideoEditIcon } from "../assets/videoEditIcon.svg";
import { ReactComponent as SquiggleIcon } from "../assets/squiggleIcon.svg";
import { ReactComponent as VideoUploadIcon } from "../assets/videoUploadIcon.svg";
import { FileUploader } from "react-drag-drop-files";
import "./VideoUpload.css";
import Questions from "./Questions";

const fileTypes = ["MP4"];
const backendPort = process.env.REACT_APP_BACKEND_PORT;

function VideoUpload({
  file,
  setFile,
  setIsUploading,
  setIsProcessing,
  setVideoData,
}) {
  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleChange = async (video) => {
    setIsUploading(true);
    setFile(video);
    setIsModalOpen(true);
  };

  const handleModalSubmit = async (data) => {
    setVideoData(data);
    setIsModalOpen(false);

    const formData = new FormData();
    formData.append("video", file);
    formData.append("isMatch", data.isMatch);
    try {
      const response = await fetch(`${backendPort}/upload`, {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        console.log("File uploaded successfully:", data);
        setIsUploading(false);
        setIsProcessing(true);
      } else {
        console.error("File upload failed:", response.statusText);
        setIsUploading(false);
      }
    } catch (error) {
      console.error("Error uploading file:", error);
      setIsUploading(false);
    }
  };

  return (
    <div className="VU-uploadContainer">
      <VideoEditIcon className="VU-videoEditIcon" />
      <SquiggleIcon className="VU-squiggleIcon" />
      <FileUploader
        classes="VU-uploadBox"
        handleChange={handleChange}
        name="file"
        types={fileTypes}
        hoverTitle=" "
      >
        <div>
          <div className="VU-uploadButton">
            <VideoUploadIcon className="VU-videoUploadIcon" />
            Upload your video
          </div>
          <div className="VU-alternative">Or drag and drop a video here</div>
        </div>
      </FileUploader>
      <Questions
        isOpen={isModalOpen}
        onRequestClose={() => setIsModalOpen(false)}
        onSubmit={handleModalSubmit}
      />
    </div>
  );
}

export default VideoUpload;
