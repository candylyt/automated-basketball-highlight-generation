import React from "react";
import { ReactComponent as VideoEditIcon } from "../assets/videoEditIcon.svg";
import { ReactComponent as SquiggleIcon } from "../assets/squiggleIcon.svg";
import { ReactComponent as VideoUploadIcon } from "../assets/videoUploadIcon.svg";
import { FileUploader } from "react-drag-drop-files";
import "./VideoUpload.css";

const fileTypes = ["MP4"];

function VideoUpload({ setFile }) {
  const handleChange = (file) => {
    setFile(file);
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
    </div>
  );
}

export default VideoUpload;
