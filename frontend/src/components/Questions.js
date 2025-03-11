import React, { useState } from "react";
import Modal from "react-modal";
import "./Questions.css";
import { validateTimestamp, convertFullTimestamp } from "./utils";

Modal.setAppElement("#root");

function Questions({ isOpen, onRequestClose, onSubmit }) {
  const [isMatch, setIsMatch] = useState(null);
  const [isSwitched, setIsSwitched] = useState(null);
  const [switchTimestamp, setSwitchTimestamp] = useState("");
  const [quarterTimestamps, setQuarterTimestamps] = useState(["00:00"]);
  const [error, setError] = useState("");

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

  const handleSubmit = (e) => {
    e.preventDefault();

    if (isSwitched && !validateTimestamp(switchTimestamp)) {
      setError("Please enter a valid timestamp in hh:mm:ss or mm:ss format!");
      return;
    }

    for (const timestamp of quarterTimestamps) {
      console.log(timestamp);
      if (timestamp != "" && !validateTimestamp(timestamp)) {
        setError(
          "Please enter valid timestamps for all quarters in hh:mm:ss or mm:ss format!"
        );
        return;
      }
    }

    const formattedTimestamps = quarterTimestamps.map(convertFullTimestamp);

    setError("");
    onSubmit({ isMatch, isSwitched, switchTimestamp, formattedTimestamps });
    onRequestClose();
  };

  const handleCancel = () => {
    setIsMatch(null);
    setIsSwitched(null);
    setSwitchTimestamp("");
    setQuarterTimestamps([""]);
    setError("");
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
                // value="Yes"
                checked={isMatch === true}
                onChange={(e) => setIsMatch(true)}
              />
            </label>
            <label>
              No
              <input
                type="radio"
                // value="No"
                checked={isMatch === false}
                onChange={(e) => setIsMatch(false)}
              />
            </label>
          </div>
        </div>
        {isMatch && (
          <div className="Question-formGroup">
            <label>2. Did the teams switch side throughout the game?</label>
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
              3. Please indicate the timestamp when the team switched side
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
                ? "4."
                : "3."
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
              quarterTimestamps.some((timestamp) => timestamp === "")
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
