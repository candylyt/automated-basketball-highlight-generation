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
  const [minutes, seconds] = timestamp.split(":");
  return parseInt(minutes) * 60 + parseInt(seconds);
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
