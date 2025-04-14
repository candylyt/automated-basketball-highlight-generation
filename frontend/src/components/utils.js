export const convertMillisecondsToTimestamp = (milliseconds) => {
  const totalSeconds = Math.floor(milliseconds / 1000);
  const hours = Math.floor(totalSeconds / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = totalSeconds % 60;

  const pad = (num) => String(num).padStart(2, "0");
  if (hours > 0) {
    return `${hours}:${pad(minutes)}:${pad(seconds)}`;
  } else {
    return `${minutes}:${pad(seconds)}`;
  }
};

export const convertTimestampToMilliseconds = (timestamp) => {
  const parts = timestamp.split(":").map(parseFloat);
  let milliseconds = 0;

  if (parts.length === 3) {
    // HH:MM:SS
    milliseconds += parts[0] * 3600 * 1000; // hours to milliseconds
    milliseconds += parts[1] * 60 * 1000; // minutes to milliseconds
    milliseconds += parts[2] * 1000; // seconds to milliseconds
  } else if (parts.length === 2) {
    // MM:SS
    milliseconds += parts[0] * 60 * 1000; // minutes to milliseconds
    milliseconds += parts[1] * 1000; // seconds to milliseconds
  }

  return milliseconds;
};

export const convertTimestampToSeconds = (timestamp) => {
  const parts = timestamp.split(":").map(parseInt);

  if (parts.length === 3) {
    const [hours, minutes, seconds] = parts;
    return hours * 3600 + minutes * 60 + seconds;
  } else {
    const [minutes, seconds] = parts;
    return minutes * 60 + seconds;
  }
};

export const validateTimestamp = (timestamp) => {
  const hhmmssPattern = /^(0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]$/;
  const mmssPattern = /^[0-5][0-9]:[0-5][0-9]$/;
  return hhmmssPattern.test(timestamp) || mmssPattern.test(timestamp);
};

export const convertTimestamp = (timestamp) => {
  const [hh, mm, ss] = timestamp.split(":");
  if (hh === "00") {
    return `${mm}:${ss}`;
  }
  return timestamp;
};

export const convertFullTimestamp = (timestamp) => {
  const parts = timestamp.split(":");
  if (parts.length == 2) {
    const [mm, ss] = parts;
    return `00:${mm}:${ss}`;
  }
  return timestamp;
};

export const sumArray = (arr) => {
  return arr.reduce((acc, num) => acc + num, 0);
};

export const captureFrame = (videoFile, frameNumber, callback) => {
  const video = document.createElement("video");
  video.src = URL.createObjectURL(videoFile);
  video.crossOrigin = "anonymous";
  video.preload = "metadata";

  video.onloadedmetadata = () => {
    const estimatedFps = 30; // You can refine this logic
    const targetTime = frameNumber / estimatedFps;
    video.currentTime = targetTime;
  };

  video.onseeked = () => {
    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    canvas.toBlob((blob) => {
      callback(blob);
    }, "image/jpeg");
  };
};
