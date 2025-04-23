import React, { useState, useEffect, useRef } from "react";
import Modal from "react-modal";
import { ReactComponent as ExportIcon } from "../assets/exportIcon.svg";
import { FFmpeg } from "@ffmpeg/ffmpeg";
import { fetchFile } from "@ffmpeg/util";
import {
  convertMillisecondsToTimestamp,
  convertTimestampToMilliseconds,
} from "./utils";
import "./Export.css";

Modal.setAppElement("#root"); // Set the root element for accessibility

const backendPort = process.env.REACT_APP_BACKEND_PORT;

const Export = ({ timestamps, video, isMatch, runId }) => {
  const [modalIsOpen, setModalIsOpen] = useState(false);
  const [selectedTimestamps, setSelectedTimestamps] = useState([]);
  const [processing, setProcessing] = useState(false);
  const [FFmpegLoaded, setFFmpegLoaded] = useState(false);
  const [highlightVideo, setHighlightVideo] = useState();

  const openModal = () => {
    setModalIsOpen(true);
  };

  const closeModal = () => {
    setModalIsOpen(false);
    setProcessing(false);
    setHighlightVideo(null);
    setSelectedTimestamps([]);
  };

  const handleTimestampSelection = (timestamp, videoId) => {
    const newEntry = [timestamp, videoId];
    setSelectedTimestamps((prevSelected) => {
      if (prevSelected.some(([ts, id]) => ts === timestamp && id === videoId)) {
        return prevSelected.filter(
          ([ts, id]) => ts !== timestamp || id !== videoId
        );
      } else {
        return [...prevSelected, newEntry];
      }
    });
  };

  const ffmpegRef = useRef(new FFmpeg());

  const handleTrim = async () => {
    const ffmpeg = ffmpegRef.current;
    setProcessing(true);

    // Sort the timestamps in ascending order
    const sortedTimestamps = [...selectedTimestamps].sort((a, b) => {
      return (
        convertTimestampToMilliseconds(a[0]) -
        convertTimestampToMilliseconds(b[0])
      );
    });

    // Update the selectedTimestamps state variable
    setSelectedTimestamps(sortedTimestamps);

    // Load both video files into FFmpeg
    await ffmpeg.writeFile("video1.mp4", await fetchFile(video.file1));
    await ffmpeg.writeFile("video2.mp4", await fetchFile(video.file2));

    // Trim the video based on each timestamp and save each clip to a temporary file
    const clipPromises = sortedTimestamps.map(([timestamp, videoId], index) => {
      const clipName = `clip-${index}.mp4`;
      const inputFile = videoId === 1 ? "video1.mp4" : "video2.mp4";
      return ffmpeg.exec([
        "-i",
        inputFile,
        "-ss",
        timestamp,
        "-t",
        "7", // duration of each clip
        "-r",
        "30",
        "-c",
        "copy",
        // "-c:v",
        // "libx264",
        // "-preset",
        // "fast",
        // "-crf",
        // "23",
        // "-c:a",
        // "aac",
        clipName,
      ]);
    });

    await Promise.all(clipPromises);

    // Create a file list for concatenation
    const concatList = sortedTimestamps
      .map((_, index) => `file clip-${index}.mp4`)
      .join("\n");
    await ffmpeg.writeFile("concat_list.txt", concatList);

    // Concatenate the clips into one video
    await ffmpeg.exec([
      "-f",
      "concat",
      "-safe",
      "0",
      "-i",
      "concat_list.txt",
      "-c",
      "copy",
      "output.mp4",
    ]);

    const data = await ffmpeg.readFile("output.mp4");

    setHighlightVideo(
      URL.createObjectURL(new Blob([data.buffer], { type: "video/mp4" }))
    );

    // Clean up temporary files
    sortedTimestamps.forEach((_, index) => {
      ffmpeg.deleteFile(`clip-${index}.mp4`);
    });
    ffmpeg.deleteFile("concat_list.txt");
    ffmpeg.deleteFile("video1.mp4");
    ffmpeg.deleteFile("video2.mp4");

    setProcessing(false);
  };

  const handleDownload = async () => {
    try {
      const response = await fetch(`${backendPort}/generate-report`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          run_id: runId,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to generate PDF");
      }

      const blob = await response.blob();
      const link = document.createElement("a");
      link.href = URL.createObjectURL(blob);
      link.download = "Basketball_Report.pdf";
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (error) {
      console.error("Error generating PDF:", error);
    }
  };

  useEffect(() => {
    const ffmpeg = ffmpegRef.current;
    ffmpeg.on();
    // ensure FFmpeg is loaded before any video processing takes place
    ffmpeg.load().then(() => setFFmpegLoaded(true));
  }, []);

  return (
    <div>
      <button className="exportButton" onClick={openModal}>
        <div>Export</div>
        <ExportIcon className="exportIcon" />
      </button>

      <Modal
        isOpen={modalIsOpen}
        onRequestClose={closeModal}
        contentLabel="Export Options"
        className="modal"
        overlayClassName="overlay"
      >
        <h2>Export Options</h2>
        <label className="stepLabel">Step 1: Select Timestamps</label>
        {isMatch ? (
          <label className="stepLabel">Team A Made-Attempts</label>
        ) : (
          <label className="stepLabel">Made-Attempts</label>
        )}
        <div className="timestampContainer">
          {timestamps.scoringTimestampsA.map(([timestamp, videoId], index) => (
            <div key={index} className="timestamp">
              <label htmlFor={`timestamp-${index}`}>{timestamp}</label>
              <input
                className="timestampCheckbox"
                type="checkbox"
                id={`timestamp-${index}`}
                value={timestamp}
                onChange={() => handleTimestampSelection(timestamp, videoId)}
              />
            </div>
          ))}
        </div>
        {isMatch ? (
          <label className="stepLabel">Team A Missed-Attempts</label>
        ) : (
          <label className="stepLabel">Missed-Attempts</label>
        )}
        <div className="timestampContainer">
          {timestamps.shootingTimestampsA.map(([timestamp, videoId], index) => (
            <div key={index} className="timestamp">
              <label htmlFor={`timestamp-${index}`}>{timestamp}</label>
              <input
                className="timestampCheckbox"
                type="checkbox"
                id={`timestamp-${index}`}
                value={timestamp}
                onChange={() => handleTimestampSelection(timestamp, videoId)}
              />
            </div>
          ))}
        </div>
        {isMatch && <label className="stepLabel">Team B Made-Attempts</label>}
        {isMatch && (
          <div className="timestampContainer">
            {timestamps.scoringTimestampsB.map(
              ([timestamp, videoId], index) => (
                <div key={index} className="timestamp">
                  <label htmlFor={`timestamp-${index}`}>{timestamp}</label>
                  <input
                    className="timestampCheckbox"
                    type="checkbox"
                    id={`timestamp-${index}`}
                    value={timestamp}
                    onChange={() =>
                      handleTimestampSelection(timestamp, videoId)
                    }
                  />
                </div>
              )
            )}
          </div>
        )}
        {isMatch && <label className="stepLabel">Team B Missed-Attempts</label>}
        {isMatch && (
          <div className="timestampContainer">
            {timestamps.shootingTimestampsB.map(
              ([timestamp, videoId], index) => (
                <div key={index} className="timestamp">
                  <label htmlFor={`timestamp-${index}`}>{timestamp}</label>
                  <input
                    className="timestampCheckbox"
                    type="checkbox"
                    id={`timestamp-${index}`}
                    value={timestamp}
                    onChange={() =>
                      handleTimestampSelection(timestamp, videoId)
                    }
                  />
                </div>
              )
            )}
          </div>
        )}

        <label className="stepLabel">Step 2: Generate Highlight</label>
        <div>
          {highlightVideo ? (
            <button
              className="regenerateButton"
              onClick={handleTrim}
              disabled={processing || selectedTimestamps.length <= 0}
            >
              {processing ? "Processing..." : "Regenerate"}
            </button>
          ) : (
            <button
              onClick={handleTrim}
              disabled={processing || selectedTimestamps.length <= 0}
            >
              {processing ? "Processing..." : "Start Generating"}
            </button>
          )}
          {highlightVideo && (
            <div className="highlightContainer">
              <video className="highlight" src={highlightVideo} controls />
            </div>
          )}
        </div>
        <label className="stepLabel">Step 3: Export Method</label>
        <a
          href={highlightVideo}
          download="highlight.mp4"
          disabled={!highlightVideo}
          className={!highlightVideo ? "disabled" : ""}
        >
          {processing ? "Processing..." : "Download"}
        </a>
        <div className="reportContainer">
          <label className="stepLabel">
            Step 4: Download Statistics Report
          </label>
          <button className="reportButton" onClick={handleDownload}>
            Download
          </button>
        </div>

        <button className="close" onClick={closeModal}>
          Close
        </button>
      </Modal>
    </div>
  );
};

export default Export;
