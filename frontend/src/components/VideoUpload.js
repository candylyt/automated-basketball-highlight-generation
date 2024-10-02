import React from "react";
import { ReactComponent as VideoEditIcon } from "../assets/videoEditIcon.svg";
import { ReactComponent as SquiggleIcon } from "../assets/squiggleIcon.svg";
import { ReactComponent as VideoUploadIcon } from "../assets/videoUploadIcon.svg";
import "./VideoUpload.css";

function VideoUpload() {
  return (
    <div className="VU-uploadContainer">
      <VideoEditIcon className="VU-videoEditIcon" />
      <SquiggleIcon className="VU-squiggleIcon" />
      <div className="VU-uploadBox">
        <div className="VU-uploadButton">
          <VideoUploadIcon className="VU-videoUploadIcon" />
          Upload your video
        </div>
        <div className="VU-alternative">Or drag and drop a video here</div>
      </div>
    </div>
  );
}

export default VideoUpload;
