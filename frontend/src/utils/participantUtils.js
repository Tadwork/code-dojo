/**
 * Utilities for generating participant identifiers and colors.
 */

// Random name components for participant display names
const ADJECTIVES = [
    'Swift', 'Clever', 'Bright', 'Bold', 'Quick',
    'Sharp', 'Keen', 'Wise', 'Noble', 'Brave',
    'Calm', 'Cool', 'Epic', 'Grand', 'Lucky',
];

const NOUNS = [
    'Coder', 'Hacker', 'Dev', 'Ninja', 'Wizard',
    'Dragon', 'Phoenix', 'Tiger', 'Eagle', 'Lion',
    'Falcon', 'Shark', 'Wolf', 'Bear', 'Hawk',
];

/**
 * Generate a random UUID-like string.
 */
export const generateUserId = () => {
    // Check if we already have a userId in localStorage
    const storedId = localStorage.getItem('codedojo_user_id');
    if (storedId) {
        return storedId;
    }

    // Generate a new UUID-like string
    const newId = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
        const r = (Math.random() * 16) | 0;
        const v = c === 'x' ? r : (r & 0x3) | 0x8;
        return v.toString(16);
    });

    localStorage.setItem('codedojo_user_id', newId);
    return newId;
};

/**
 * Generate a random display name for a participant.
 */
export const generateDisplayName = () => {
    // Check if we already have a display name in localStorage
    const storedName = localStorage.getItem('codedojo_display_name');
    if (storedName) {
        return storedName;
    }

    const adjective = ADJECTIVES[Math.floor(Math.random() * ADJECTIVES.length)];
    const noun = NOUNS[Math.floor(Math.random() * NOUNS.length)];
    const newName = `${adjective} ${noun}`;

    localStorage.setItem('codedojo_display_name', newName);
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
    const cleanHex = hex.replace('#', '');
    const r = parseInt(cleanHex.substring(0, 2), 16);
    const g = parseInt(cleanHex.substring(2, 4), 16);
    const b = parseInt(cleanHex.substring(4, 6), 16);
    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
};
