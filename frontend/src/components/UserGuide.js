import React, { useState } from "react";
import Modal from "react-modal";
import sample1 from "../assets/sample_1.png";
import sample2 from "../assets/sample_2.png";
import "./UserGuide.css";

Modal.setAppElement("#root");

const UserGuide = ({ isOpen, onRequestClose, onSubmit }) => {
  const ugcontent = [
    "For highlight generation ONLY, you don't need to use stationary camera.",
    "For both highlight generation and data analytics, only stationary cameras are allowed. Please ensure that the camera's location is FIXED throughout the video. It should NOT be moved or rotated.",
    "Please position the camera at a height of 2.5 meters or higher. The 4 corners of the paint/key area should be clearly visible in the video.",
    "The default processing pipeline supports only half-court videos. If you have a full-court video, you will be prompted to upload two separate videos.",
    "Please ensure that the camera angle is similar to the samples below:",
    "The video should be in MP4 format. The maximum file size is 5GB.",
    "The video should be at least 30 seconds long and no longer than 2 hours.",
    "The video should be in landscape mode. Portrait videos will not be accepted.",
    "If two footages are uploaded for full-court matches, they MUST have IDENTICAL codecs to ensure proper concatenation during highlight generation.",
    "Team-based statistics are only available for full-court matches. For half-court matches, only overall statistics that include both teams will be provided.",
    "We use FIBA court dimensions for all calculations. There might be slight deviation if your court dimensions differ.",
    "The video will be discarded after all processing is completed. We do not store any videos on our servers.",
  ];

  const [isRead, setIsRead] = useState(false);

  const handleChange = (e) => {
    setIsRead(e.target.checked);
  };

  const handleCancel = () => {
    setIsRead(false);
    onRequestClose();
  };

  return (
    <Modal
      isOpen={isOpen}
      onRequestClose={onRequestClose}
      onSubmit={onSubmit}
      className="UG-modal"
      overlayClassName="UG-overlay"
    >
      <div className="UG-header">
        Important User Guidelines & Privacy Notice
      </div>
      <ol className="UG-content">
        {ugcontent.map((item, index) => (
          <li key={index} className="UG-points">
            {item}
            {index === 3 && (
              <div className="UG-sampleImages">
                <img
                  src={sample1}
                  alt="Sample Image 1"
                  style={{ marginTop: "8px", width: "45%" }}
                />
                <img
                  src={sample2}
                  alt="Sample Image 2"
                  style={{ marginTop: "8px", width: "45%" }}
                />
              </div>
            )}
          </li>
        ))}
      </ol>
      <label className="UG-checkbox">
        <input
          type="checkbox"
          checked={isRead}
          onChange={handleChange}
          className="UG-box"
        />
        I have read and agree to the user guidelines.
      </label>
      <div className="UG-buttonContainer">
        <button type="button" onClick={handleCancel}>
          Cancel
        </button>
        <button
          type="button"
          onClick={() => {
            onSubmit();
            setIsRead(false);
          }}
          disabled={isRead == false}
        >
          Submit
        </button>
      </div>
    </Modal>
  );
};

export default UserGuide;
