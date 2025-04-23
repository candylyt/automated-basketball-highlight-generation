import React, { useEffect, useState } from "react";
import Modal from "react-modal";
import "./Questions.css";
import { validateTimestamp, convertFullTimestamp, captureFrame } from "./utils";
import LabelCourt from "./LabelCourt";
import { FileUploader } from "react-drag-drop-files";
import { ReactComponent as VideoUploadIcon } from "../assets/videoUploadIcon.svg";

Modal.setAppElement("#root");
const fileTypes = ["MP4"];

function Questions({
  isOpen,
  frameUrl1,
  frameUrl2,
  setFrameUrl1,
  setFrameUrl2,
  file1,
  file2,
  setFile2,
  onRequestClose,
  onSubmit,
}) {
  const [isMatch, setIsMatch] = useState(null);
  const [isSwitched, setIsSwitched] = useState(null);
  const [switchTimestamp, setSwitchTimestamp] = useState("");
  const [quarterTimestamps, setQuarterTimestamps] = useState(["00:00"]);
  const [error, setError] = useState("");
  const [points1, setPoints1] = useState([]);
  const [points2, setPoints2] = useState([]);
  const [imageDimensions1, setImageDimensions1] = useState([]);
  const [imageDimensions2, setImageDimensions2] = useState([]);

  const handleAddQuarter = () => {
    setQuarterTimestamps([...quarterTimestamps, ""]);
  };

  const handleDeleteQuarter = (index) => {
    const newQuarterTimestamps = quarterTimestamps.filter(
      (_, i) => i !== index
    );
    setQuarterTimestamps(newQuarterTimestamps);
  };

  const handleQuarterChange = (index, value) => {
    const newQuarterTimestamps = [...quarterTimestamps];
    newQuarterTimestamps[index] = value;
    setQuarterTimestamps(newQuarterTimestamps);
  };

  const updateImageDimensions = (camera, width, height) => {
    if (camera === 1) {
      setImageDimensions1([width, height]);
    } else if (camera === 2) {
      setImageDimensions2([width, height]);
    }
  };

  const handleChange = async (video) => {
    setFile2(video);
    captureFrame(video, 100, (frameBlob) => {
      const imageUrl = URL.createObjectURL(frameBlob);
      setFrameUrl2(imageUrl);
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    if (isSwitched && !validateTimestamp(switchTimestamp)) {
      setError("Please enter a valid timestamp in hh:mm:ss or mm:ss format!");
      return;
    }

    for (const timestamp of quarterTimestamps) {
      if (timestamp != "" && !validateTimestamp(timestamp)) {
        setError(
          "Please enter valid timestamps for all quarters in hh:mm:ss or mm:ss format!"
        );
        return;
      }
    }

    const formattedTimestamps = quarterTimestamps.map(convertFullTimestamp);
    const formattedSwitchTimestamps = convertFullTimestamp(switchTimestamp);

    setError("");
    onSubmit({
      isMatch,
      isSwitched,
      formattedSwitchTimestamps,
      formattedTimestamps,
      points1,
      points2,
      imageDimensions1,
      imageDimensions2,
    });
    onRequestClose();
  };

  const handleCancel = () => {
    setIsMatch(null);
    setIsSwitched(null);
    setSwitchTimestamp("");
    setQuarterTimestamps(["00:00"]);
    setError("");
    setPoints1([]);
    setPoints2([]);
    setFile2(null);
    setFrameUrl2(null);
    setImageDimensions1([]);
    setImageDimensions2([]);
    onRequestClose();
  };

  return (
    <Modal
      isOpen={isOpen}
      onRequestClose={onRequestClose}
      contentLabel="Video Configuration"
      className="Question-modal"
      overlayClassName="Question-overlay"
    >
      <div className="Question-header">Configuration Settings</div>
      <form onSubmit={handleSubmit}>
        <div className="Question-formGroup">
          <label>1. Is this a full-court match?</label>
          <div className="Question-radioGroup">
            <label>
              Yes
              <input
                type="radio"
                checked={isMatch === true}
                onChange={(e) => setIsMatch(true)}
              />
            </label>
            <label>
              No
              <input
                type="radio"
                checked={isMatch === false}
                onChange={(e) => setIsMatch(false)}
              />
            </label>
          </div>
        </div>
        {isMatch && (
          <div className="Question-formGroup">
            <label>
              2. Please upload the game footage of the other half court.
            </label>
            {file2 ? (
              <div className="Question-videoContainer">
                <video controls className="Question-video">
                  <source src={URL.createObjectURL(file2)} type={file2.type} />
                </video>
                <button
                  className="Question-reupload"
                  onClick={() => setFile2(null)}
                >
                  Reupload
                </button>
              </div>
            ) : (
              <FileUploader
                classes="Question-uploadBox"
                handleChange={handleChange}
                name="file"
                types={fileTypes}
                hoverTitle=" "
              >
                <div>
                  <div className="Question-uploadButton">
                    <VideoUploadIcon className="Question-videoUploadIcon" />
                    Upload your video
                  </div>
                  <div className="Question-alternative">
                    Or drag and drop a video here
                  </div>
                </div>
              </FileUploader>
            )}

            <label>3. Did the teams switch side throughout the game?</label>
            <div className="Question-radioGroup">
              <label>
                Yes
                <input
                  type="radio"
                  checked={isSwitched === true}
                  onChange={(e) => setIsSwitched(true)}
                />
              </label>
              <label>
                No
                <input
                  type="radio"
                  checked={isSwitched === false}
                  onChange={(e) => setIsSwitched(false)}
                />
              </label>
            </div>
          </div>
        )}

        {isSwitched && (
          <div className="Question-formGroup">
            <label>
              4. Please indicate the timestamp when the team switched side
              (e.g., 30:00).
            </label>
            <input
              className="Question-switchTimestamp"
              type="text"
              value={switchTimestamp}
              onChange={(e) => setSwitchTimestamp(e.target.value)}
            />
          </div>
        )}
        <div className="Question-formGroup">
          <label>
            {`${
              isMatch === false || !isMatch
                ? "2."
                : isSwitched === true
                ? "5."
                : "4."
            } Please indicate the starting timestamp for each quarter (if any).`}
          </label>
          <div className="Question-quarters">
            {quarterTimestamps.map((timestamp, index) => (
              <div key={index} className="Question-quarterGroup">
                <input
                  className="Question-quarter"
                  type="text"
                  value={timestamp}
                  placeholder={`Quarter ${index + 1}`}
                  onChange={(e) => handleQuarterChange(index, e.target.value)}
                />
                {index !== 0 && (
                  <button
                    className="Question-delete"
                    type="button"
                    onClick={() => handleDeleteQuarter(index)}
                  >
                    Delete
                  </button>
                )}
              </div>
            ))}
          </div>

          <button type="button" onClick={handleAddQuarter}>
            Add Quarter
          </button>
        </div>
        {frameUrl1 && file1 && (
          <LabelCourt
            video={file1}
            camera={1}
            imageUrl={frameUrl1}
            points={points1}
            setPoints={setPoints1}
            setFrameUrl={setFrameUrl1}
            updateImageDimensions={updateImageDimensions}
          />
        )}
        {frameUrl2 && file2 && (
          <LabelCourt
            video={file2}
            camera={2}
            imageUrl={frameUrl2}
            points={points2}
            setPoints={setPoints2}
            setFrameUrl={setFrameUrl2}
            updateImageDimensions={updateImageDimensions}
          />
        )}
        <div className="Question-error">{error}</div>
        <div className="Question-buttonContainer">
          <button type="button" onClick={handleCancel}>
            Cancel
          </button>
          <button
            type="submit"
            disabled={
              isMatch == null ||
              (isMatch && isSwitched == null) ||
              (isSwitched && switchTimestamp === "") ||
              quarterTimestamps.some((timestamp) => timestamp === "") ||
              points1.length !== 4 ||
              (isMatch && file2 == null) ||
              (isMatch && points2.length !== 4)
            }
          >
            Submit
          </button>
        </div>
      </form>
    </Modal>
  );
}

export default Questions;
