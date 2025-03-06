import React, { useEffect, useRef, useState } from "react";
import { ReactComponent as VideoEditIcon } from "../assets/videoEditIcon.svg";
import { ReactComponent as SquiggleIcon } from "../assets/squiggleIcon.svg";
import { ReactComponent as VideoUploadIcon } from "../assets/videoUploadIcon.svg";
import { FileUploader } from "react-drag-drop-files";
import { FFmpeg } from "@ffmpeg/ffmpeg";
import { fetchFile } from "@ffmpeg/util";
import "./VideoUpload.css";

const fileTypes = ["MP4"];
const backendPort = process.env.REACT_APP_BACKEND_PORT;

function VideoUpload({ setFile, setIsUploading, setIsProcessing }) {
  const [ffmpeg, setFfmpeg] = useState(null);
  const [compressionStatus, setCompressionStatus] = useState("");

  useEffect(() => {
    // Initialize FFmpeg
    const loadFFmpeg = async () => {
      const ffmpegInstance = new FFmpeg();

      // Log FFmpeg messages
      ffmpegInstance.on("log", ({ message }) => {
        console.log(message);
      });

      // Load FFmpeg from CDN
      try {
        await ffmpegInstance.load({
          coreURL:
            "https://unpkg.com/@ffmpeg/core@0.12.4/dist/umd/ffmpeg-core.js",
          wasmURL:
            "https://unpkg.com/@ffmpeg/core@0.12.4/dist/umd/ffmpeg-core.wasm",
        });
        setFfmpeg(ffmpegInstance);
      } catch (error) {
        console.error("Error loading FFmpeg:", error);
      }
    };

    loadFFmpeg();
  }, []);

  const compressVideo = async (file) => {
    try {
      setCompressionStatus("Compressing video...");

      // Write the file to FFmpeg's file system
      await ffmpeg.writeFile("input.mp4", await fetchFile(file));
      console.log("File loaded into FFmpeg");

      // Run FFmpeg compression command
      await ffmpeg.exec([
        "-i",
        "input.mp4",
        "-vf",
        "scale=640:-1",
        "-r",
        "30",
        "-c:v",
        "libx264",
        "-crf",
        "28",
        "-preset",
        "faster",
        "output.mp4",
      ]);
      console.log("Video compression completed");

      // Read the compressed file
      const data = await ffmpeg.readFile("output.mp4");
      const compressedBlob = new Blob([data.buffer], { type: "video/mp4" });

      setCompressionStatus("Compression complete");
      return compressedBlob;
    } catch (error) {
      console.error("Compression failed:", error);
      setCompressionStatus("Compression failed");
      throw error;
    }
  };

  const handleChange = async (file) => {
    setIsUploading(true);
    setFile(file);

    try {
      // Compress the video first
      const compressedVideo = await compressVideo(file);

      // Create FormData with compressed video
      const formData = new FormData();
      formData.append("video", compressedVideo, "compressed.mp4");

      // Upload the compressed video
      const response = await fetch(`${backendPort}/upload`, {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        console.log("File uploaded successfully:", data);
        setIsUploading(false);
        setIsProcessing(true);
      } else {
        console.error("File upload failed:", response.statusText);
        setIsUploading(false);
      }
    } catch (error) {
      console.error("Error processing/uploading file:", error);
      setIsUploading(false);
    }
  };

  return (
    <div className="VU-uploadContainer">
      <VideoEditIcon className="VU-videoEditIcon" />
      <SquiggleIcon className="VU-squiggleIcon" />
      <FileUploader
        classes="VU-uploadBox"
        handleChange={handleChange}
        name="file"
        types={fileTypes}
        hoverTitle=" "
      >
        <div>
          <div className="VU-uploadButton">
            <VideoUploadIcon className="VU-videoUploadIcon" />
            Upload your video
          </div>
          <div className="VU-alternative">Or drag and drop a video here</div>
          {compressionStatus && (
            <div className="VU-status">{compressionStatus}</div>
          )}
        </div>
      </FileUploader>
    </div>
  );
}

export default VideoUpload;
