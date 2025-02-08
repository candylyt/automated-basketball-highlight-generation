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

const Export = ({ timestamps, video }) => {
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

  const handleTimestampSelection = (timestamp) => {
    setSelectedTimestamps((prevSelected) => {
      if (prevSelected.includes(timestamp)) {
        return prevSelected.filter((t) => t !== timestamp);
      } else {
        return [...prevSelected, timestamp];
      }
    });
  };

  const ffmpegRef = useRef(new FFmpeg());

  const handleTrim = async () => {
    console.log("handleTrim");
    const ffmpeg = ffmpegRef.current;
    setProcessing(true);

    // Sort the timestamps in ascending order
    const sortedTimestamps = [...selectedTimestamps].sort((a, b) => {
      return (
        convertTimestampToMilliseconds(a) - convertTimestampToMilliseconds(b)
      );
    });

    // Update the selectedTimestamps state variable
    setSelectedTimestamps(sortedTimestamps);

    // Load the video file
    await ffmpeg.writeFile("input.mp4", await fetchFile(video));

    // Trim the video based on each timestamp and save each clip to a temporary file
    const clipPromises = sortedTimestamps.map((timestamp, index) => {
      const clipName = `clip-${index}.mp4`;
      return ffmpeg.exec([
        "-i",
        "input.mp4",
        "-ss",
        timestamp,
        "-t",
        "5",
        "-c",
        "copy",
        clipName,
      ]);
    });

    await Promise.all(clipPromises);

    // Create a file list for concatenation
    const concatList = sortedTimestamps
      .map((timestamp, index) => `file clip-${index}.mp4`)
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
    sortedTimestamps.forEach((timestamp, index) => {
      ffmpeg.deleteFile(`clip-${index}.mp4`);
    });
    ffmpeg.deleteFile("concat_list.txt");
    ffmpeg.deleteFile("input.mp4");

    setProcessing(false);
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
        <div className="timestampContainer">
          {timestamps.map((timestamp, index) => (
            <div key={index} className="timestamp">
              <label htmlFor={`timestamp-${index}`}>{timestamp}</label>
              <input
                className="timestampCheckbox"
                type="checkbox"
                id={`timestamp-${index}`}
                value={timestamp}
                onChange={() => handleTimestampSelection(timestamp)}
              />
            </div>
          ))}
        </div>

        <label className="stepLabel">Step 2: Generate Highlight</label>
        <div>
          {!highlightVideo && (
            <button
              onClick={handleTrim}
              disabled={processing || selectedTimestamps.length <= 0}
            >
              {processing ? "Processing..." : "Start"}
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
        <button className="close" onClick={closeModal}>
          Close
        </button>
      </Modal>
    </div>
  );
};

export default Export;
