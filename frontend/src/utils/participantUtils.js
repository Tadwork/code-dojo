/**
 * Utilities for generating participant identifiers and colors.
 */

// Random name components for participant display names
const ADJECTIVES = [
  "Swift",
  "Clever",
  "Bright",
  "Bold",
  "Quick",
  "Sharp",
  "Keen",
  "Wise",
  "Noble",
  "Brave",
  "Calm",
  "Cool",
  "Epic",
  "Grand",
  "Lucky",
];

const NOUNS = [
  "Coder",
  "Hacker",
  "Dev",
  "Ninja",
  "Wizard",
  "Dragon",
  "Phoenix",
  "Tiger",
  "Eagle",
  "Lion",
  "Falcon",
  "Shark",
  "Wolf",
  "Bear",
  "Hawk",
];

const USER_ID_STORAGE_KEY = "codedojo_user_id";
const DISPLAY_NAME_STORAGE_KEY = "codedojo_display_name";

const generateFallbackUserId = () =>
  "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, (char) => {
    const randomValue = (Math.random() * 16) | 0;
    const value = char === "x" ? randomValue : (randomValue & 0x3) | 0x8;
    return value.toString(16);
  });

export const sanitizeForCssContent = (value) =>
  value.replace(/['"\\]/g, "\\$&");

/**
 * Generate a random UUID-like string.
 */
export const generateUserId = () => {
  const storedId = localStorage.getItem(USER_ID_STORAGE_KEY);
  if (storedId) {
    return storedId;
  }

  const newId = window.crypto?.randomUUID?.() || generateFallbackUserId();
  localStorage.setItem(USER_ID_STORAGE_KEY, newId);
  return newId;
};

/**
 * Generate a random display name for a participant.
 */
export const generateDisplayName = () => {
  const storedName = localStorage.getItem(DISPLAY_NAME_STORAGE_KEY);
  if (storedName) {
    return storedName;
  }

  const adjective = ADJECTIVES[Math.floor(Math.random() * ADJECTIVES.length)];
  const noun = NOUNS[Math.floor(Math.random() * NOUNS.length)];
  const newName = `${adjective} ${noun}`;

  localStorage.setItem(DISPLAY_NAME_STORAGE_KEY, newName);
  return newName;
};

/**
 * Get the participant's userId and displayName.
 * Generates new ones if they don't exist.
 */
export const getParticipantInfo = () => {
  return {
    userId: generateUserId(),
    displayName: generateDisplayName(),
  };
};

/**
 * Convert a hex color to RGBA with opacity.
 * @param {string} hex - Hex color string (with or without #)
 * @param {number} alpha - Opacity value 0-1
 * @returns {string} RGBA color string
 */
export const hexToRgba = (hex, alpha = 1) => {
  const cleanHex = hex.replace("#", "");
  if (!/^[0-9A-Fa-f]{6}$/.test(cleanHex)) {
    return `rgba(0, 0, 0, ${alpha})`;
  }

  const r = parseInt(cleanHex.substring(0, 2), 16);
  const g = parseInt(cleanHex.substring(2, 4), 16);
  const b = parseInt(cleanHex.substring(4, 6), 16);
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
};
