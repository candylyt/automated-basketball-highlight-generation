import React, { useState } from "react";
import { ReactComponent as VideoEditIcon } from "../assets/videoEditIcon.svg";
import { ReactComponent as SquiggleIcon } from "../assets/squiggleIcon.svg";
import { ReactComponent as VideoUploadIcon } from "../assets/videoUploadIcon.svg";
import { FileUploader } from "react-drag-drop-files";
import { captureFrame } from "./utils";
import "./VideoUpload.css";
import Questions from "./Questions";
import UserGuide from "./UserGuide";

const fileTypes = ["MP4"];
const backendPort = process.env.REACT_APP_BACKEND_PORT;

function VideoUpload({
  file1,
  file2,
  setFile1,
  setFile2,
  setIsUploading,
  setIsProcessing,
  setVideoData,
}) {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isGuideModalOpen, setIsGuideModalOpen] = useState(false);
  const [frameUrl1, setFrameUrl1] = useState(null);
  const [frameUrl2, setFrameUrl2] = useState(null);

  const handleChange = async (video) => {
    setIsUploading(true);
    setFile1(video);
    captureFrame(video, 100, (frameBlob) => {
      const imageUrl = URL.createObjectURL(frameBlob);
      setFrameUrl1(imageUrl);
      setIsGuideModalOpen(true);
    });
    // setIsGuideModalOpen(true);
    // setIsModalOpen(true);
  };

  const handleModalSubmit = async (videoData) => {
    setVideoData(videoData);
    setIsModalOpen(false);

    const formData = new FormData();
    formData.append("video1", file1);
    formData.append("video2", file2);
    formData.append("isMatch", videoData.isMatch);
    formData.append("isSwitched", videoData.isSwitched);
    formData.append("switchTimestamp", videoData.switchTimestamp);
    formData.append("quarterTimestamps", videoData.formattedTimestamps);
    formData.append("points1", videoData.points1);
    formData.append("points2", videoData.points2);
    formData.append("imageDimensions1", videoData.imageDimensions1);
    formData.append("imageDimensions2", videoData.imageDimensions2);

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
      <UserGuide
        isOpen={isGuideModalOpen}
        onRequestClose={() => setIsGuideModalOpen(false)}
        onSubmit={() => {
          setIsGuideModalOpen(false);
          setIsModalOpen(true);
        }}
      />
      <Questions
        isOpen={isModalOpen}
        frameUrl1={frameUrl1}
        frameUrl2={frameUrl2}
        setFrameUrl1={setFrameUrl1}
        setFrameUrl2={setFrameUrl2}
        file1={file1}
        file2={file2}
        setFile2={setFile2}
        onRequestClose={() => {
          setIsModalOpen(false);
        }}
        onSubmit={handleModalSubmit}
      />
    </div>
  );
}

export default VideoUpload;
