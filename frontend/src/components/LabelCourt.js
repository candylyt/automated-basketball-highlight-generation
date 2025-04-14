import React, { useState, useEffect, useRef } from "react";
import court_topRight from "../assets/court-topRight.png";
import court_topLeft from "../assets/court-topLeft.png";
import court_bottomRight from "../assets/court-bottomRight.png";
import court_bottomLeft from "../assets/court-bottomLeft.png";
import { captureFrame } from "./utils";
import "./LabelCourt.css";

const PaintAreaLabeler = ({
  video,
  camera,
  imageUrl,
  points,
  setPoints,
  setFrameUrl,
  updateImageDimensions,
}) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [currentFrame, setCurrentFrame] = useState(100);

  const prompts = [
    "Click to label the *Bottom Left* corner.",
    "Click to label the *Bottom Right* corner.",
    "Click to label the *Top Left* corner.",
    "Click to label the *Top Right* corner.",
  ];

  const totalFrames = Math.floor(video.duration * 30);

  const handleChangeFrame = (direction) => {
    if (direction === "prev") {
      if (currentFrame - 1 < 0) {
        return;
      }
      captureFrame(video, currentFrame - 1, (frameBlob) => {
        const imageUrl = URL.createObjectURL(frameBlob);
        setCurrentFrame(currentFrame - 1);
        setFrameUrl(imageUrl);
      });
    } else {
      if (currentFrame + 1 <= totalFrames) {
        return;
      }
      captureFrame(video, currentFrame + 1, (frameBlob) => {
        const imageUrl = URL.createObjectURL(frameBlob);
        setCurrentFrame(currentFrame + 1);
        setFrameUrl(imageUrl);
      });
    }
  };
  const handleImageClick = (e) => {
    if (currentStep >= 4) return;

    const rect = e.target.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    const newPoints = [...points, [x, y]];
    setPoints(newPoints);
    setCurrentStep(currentStep + 1);

    if (currentStep + 1 === 4) {
      const { width, height } = e.target.getBoundingClientRect();
      updateImageDimensions(camera, width, height);
    }
  };

  const handleReset = () => {
    setPoints([]);
    setCurrentStep(0);
  };

  return (
    <div className="p-4 flex flex-col items-center gap-4">
      {camera === 1 && <h2 className="Court-header">Label Paint Area</h2>}
      {camera === 1 && (
        <p className="Court-instructions">
          Instructions: Please click on the four corners of the paint area/key
          area in the following order: Bottom Left → Bottom Right → Top Left →
          Top Right.
        </p>
      )}
      <div
        className="Court-prompt"
        style={{ color: currentStep === 4 && "green" }}
      >
        <p>Camera Angle {camera} - &nbsp;</p>
        <p>Step {currentStep + 1}: &nbsp;</p>
        <p>{prompts[currentStep] || "All points labeled!"}</p>
        <button type="button" className="Court-button" onClick={handleReset}>
          Reset
        </button>
      </div>

      <div className="Court-image">
        <img src={imageUrl} alt="Uploaded court" onClick={handleImageClick} />
        {points.map(([x, y], i) => (
          <div
            key={i}
            className="Court-dot"
            style={{
              top: y,
              left: x,
            }}
          />
        ))}
        {currentStep == 0 && (
          <img src={`${court_bottomLeft}?v=${Date.now()}`} />
        )}
        {currentStep == 1 && (
          <img src={`${court_bottomRight}?v=${Date.now()}`} />
        )}
        {currentStep == 2 && <img src={`${court_topLeft}?v=${Date.now()}`} />}
        {currentStep == 3 && <img src={`${court_topRight}?v=${Date.now()}`} />}
      </div>
      <div className="Court-frameSelection">
        <div
          className="Court-frameButton"
          onClick={() => handleChangeFrame("prev")}
        >
          Previous Frame
        </div>
        <div
          className="Court-frameButton"
          onClick={() => handleChangeFrame("next")}
        >
          Next Frame
        </div>
      </div>
    </div>
  );
};

export default PaintAreaLabeler;
