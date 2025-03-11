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

const Export = ({ timestamps, video, isMatch }) => {
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

  const handleDownload = async () => {
    try {
      const response = await fetch(`${backendPort}/generate-report`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          game_summary: {
            Date: "February 16, 2025",
            Venue: "Staples Center",
            Teams: "Team A vs Team B",
            Final_Score: "102 - 97",
          },
          field_goals_stats: {
            FGM: [38, 35],
            FGA: [82, 78],
            FG_Percent: ["46.3%", "44.9%"],
            FTM: [20, 18],
            FTA: [24, 22],
            FT_Percent: ["83.3%", "81.8%"],
            ThreePM: [6, 7],
            ThreePA: [22, 25],
            ThreeP_Percent: ["27.3%", "28.0%"],
            eFG: ["50.6%", "49.5%"],
            TS: ["55.4%", "54.2%"],
          },
          shot_types_stats: {
            Contested_Made: [10, 8],
            Contested_Attempted: [25, 20],
            Contested_Percent: ["40%", "40%"],
            Uncontested_Made: [28, 27],
            Uncontested_Attempted: [57, 58],
            Uncontested_Percent: ["49.1%", "46.6%"],
            Total_Made: [38, 35],
            Total_Attempted: [82, 78],
            Total_Percent: ["46.3%", "44.9%"],
          },
          shot_zones_stats: {
            Paint_Area_Made: [10, 8],
            Paint_Area_Attempted: [25, 20],
            Paint_Area_Percent: ["40%", "40%"],
            Mid_Range_Made: [28, 27],
            Mid_Range_Attempted: [57, 58],
            Mid_Range_Percent: ["49.1%", "46.6%"],
            Three_Point_Made: [38, 35],
            Three_Point_Attempted: [82, 78],
            Three_Point_Percent: ["46.3%", "44.9%"],
          },
          match: true,
          quarter_scores: {
            Q1: [28, 24],
            Q2: [26, 27],
            Q3: [22, 24],
            Q4: [26, 22],
          },
          quarter_percentages: {
            Q1: [45.2, 40.8],
            Q2: [42.5, 38.7],
            Q3: [47.1, 41.3],
            Q4: [50.8, 44.2],
          },
          shot_data: [
            [4, 24, "A"],
            [11, 25, "A"],
            [6, 20, "A"],
            [4, 25, "A"],
            [5, 22, "A"],
            [3, 4, "B"],
            [10, 5, "B"],
            [7, 6, "B"],
            [9, 3, "B"],
            [6, 8, "B"],
          ],
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
          <label className="stepLabel">Team A Scoring Moments</label>
        ) : (
          <label className="stepLabel">Scoring Moments</label>
        )}
        <div className="timestampContainer">
          {timestamps.scoringTimestampsA.map((timestamp, index) => (
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
        {isMatch ? (
          <label className="stepLabel">Team A Shooting Moments</label>
        ) : (
          <label className="stepLabel">Shooting Moments</label>
        )}
        <div className="timestampContainer">
          {timestamps.shootingTimestampsA.map((timestamp, index) => (
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
        {isMatch && <label className="stepLabel">Team B Scoring Moments</label>}
        {isMatch && (
          <div className="timestampContainer">
            {timestamps.scoringTimestampsB.map((timestamp, index) => (
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
        )}
        {isMatch && (
          <label className="stepLabel">Team B Shooting Moments</label>
        )}
        {isMatch && (
          <div className="timestampContainer">
            {timestamps.shootingTimestampsB.map((timestamp, index) => (
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
        )}

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
