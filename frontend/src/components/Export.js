import React, { useState, useRef } from "react";
import Modal from "react-modal";
import {
  WhatsappShareButton,
  WhatsappIcon,
  InstagramShareButton,
  InstagramIcon,
} from "react-share";
import { ReactComponent as ExportIcon } from "../assets/exportIcon.svg";
import { FFmpeg } from "@ffmpeg/ffmpeg";
import { fetchFile, toBlobURL } from "@ffmpeg/util";
import "./Export.css";

Modal.setAppElement("#root"); // Set the root element for accessibility

const Export = ({ timestamps, video }) => {
  const [modalIsOpen, setModalIsOpen] = useState(false);
  const [timestamp, setTimestamp] = useState([]);
  const [selectedTimestamps, setSelectedTimestamps] = useState([]);
  const [processing, setProcessing] = useState(false);
  const [loadFFmpeg, setLoadFFmpeg] = useState(false);

  const ffmpegRef = useRef(new FFmpeg());
  const messageRef = (useRef < HTMLParagraphElement) | (null > null);

  const openModal = () => {
    setModalIsOpen(true);
  };

  const closeModal = () => {
    setModalIsOpen(false);
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

  // initialize the ffmpeg library
  const load = async () => {
    const baseURL = "https://unpkg.com/@ffmpeg/core-mt@0.12.10/dist/esm";
    const ffmpeg = ffmpegRef.current;
    ffmpeg.on("log", ({ message }) => {
      if (messageRef.current) messageRef.current.innerHTML = message;
    });
    // toBlobURL is used to bypass CORS issue, urls with the same
    // domain can be used directly.
    await ffmpeg.load({
      coreURL: await toBlobURL(`${baseURL}/ffmpeg-core.js`, "text/javascript"),
      wasmURL: await toBlobURL(
        `${baseURL}/ffmpeg-core.wasm`,
        "application/wasm"
      ),
      workerURL: await toBlobURL(
        `${baseURL}/ffmpeg-core.worker.js`,
        "text/javascript"
      ),
    });
    setLoadFFmpeg(true);
  };

  const generateHighlightVideo = async () => {
    setProcessing(true);
    if (!loadFFmpeg) {
      await load();
    }
    const ffmpeg = ffmpegRef.current;
    ffmpeg.FS("writeFile", "input.mp4", await fetchFile(video));
    const commands = [];
    selectedTimestamps.forEach((timestamp, index) => {
      const outputFile = `clip${index}.mp4`;
      commands.push(
        "-i",
        "input.mp4",
        "-ss",
        timestamp,
        "-t",
        "3",
        "-c",
        "copy",
        outputFile
      );
    });

    for (let i = 0; i < commands.length; i += 8) {
      await ffmpeg.run(...commands.slice(i, i + 8));
    }

    const concatList = selectedTimestamps
      .map((_, index) => `file 'clip${index}.mp4'`)
      .join("\n");
    ffmpeg.FS("writeFile", "concat_list.txt", concatList);

    await ffmpeg.run(
      "-f",
      "concat",
      "-safe",
      "0",
      "-i",
      "concat_list.txt",
      "-c",
      "copy",
      "output.mp4"
    );

    const fileData = await ffmpeg.FS("readFile", "output.mp4");
    const data = new Uint8Array(fileData);
    const url = URL.createObjectURL(
      new Blob([data.buffer], { type: "video/mp4" })
    );
    const a = document.createElement("a");
    a.href = url;
    a.download = "highlight.mp4";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    setProcessing(false);
  };

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

        <label className="stepLabel">Step 2: Export Methods</label>
        <div>
          <button onClick={generateHighlightVideo} disabled={processing}>
            {processing ? "Processing..." : "Save Locally"}
          </button>
          {/* <WhatsappShareButton url={`https://example.com/highlight?timestamp=${timestamp}`}>
            <WhatsappIcon size={32} round />
          </WhatsappShareButton>
          <InstagramShareButton url={`https://example.com/highlight?timestamp=${timestamp}`}>
            <InstagramIcon size={32} round />
          </InstagramShareButton> */}
        </div>
        <button onClick={closeModal}>Close</button>
      </Modal>
    </div>
  );
};

export default Export;
