import React, { useState } from "react";
import Modal from "react-modal";
import "./Questions.css";

Modal.setAppElement("#root");

function Questions({ isOpen, onRequestClose, onSubmit }) {
  const [isMatch, setIsMatch] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({ isMatch });
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
        <button type="submit">Submit</button>
      </form>
    </Modal>
  );
}

export default Questions;
