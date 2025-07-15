// State variables
let totalDetections = 0;
let sessionStartTime = null;
let sessionTime = 0; // in seconds
let sessionTimer = null;
let totalDistance = 0;
let distanceSamples = 0;
let gestureHistory = [];

// --- Core Functions ---

/**
 * Starts a new session, resetting all statistics and starting the timer.
 */
export function startSession() {
    resetState();
    sessionStartTime = new Date();

    // Start the session timer
    sessionTimer = setInterval(() => {
        sessionTime = Math.floor((new Date() - sessionStartTime) / 1000);
        // Optional: Add a callback to update the UI in real-time
        if (window.updateStatsUI) {
            window.updateStatsUI({ sessionTime });
        }
    }, 1000);

    console.log("Session started");
}

/**
 * Stops the current session and freezes the timer.
 */
export function stopSession() {
    if (sessionTimer) {
        clearInterval(sessionTimer);
        sessionTimer = null;
    }
    console.log("Session stopped");
}

/**
 * Resets all statistics to their initial state.
 */
export function resetState() {
    totalDetections = 0;
    sessionStartTime = null;
    sessionTime = 0;
    if (sessionTimer) {
        clearInterval(sessionTimer);
        sessionTimer = null;
    }
    totalDistance = 0;
    distanceSamples = 0;
    gestureHistory = [];
    console.log("State reset");
}

/**
 * Records a new gesture detection, updating all relevant stats.
 * @param {object} detection - The detection result from the server.
 *                             Expected to have `gesture` and `distance`.
 */
export function recordDetection(detection) {
    if (!detection || !detection.gesture) {
        return;
    }

    // 1. Increment total detections
    totalDetections++;

    // 2. Update average distance
    if (typeof detection.distance === 'number') {
        totalDistance += detection.distance;
        distanceSamples++;
    }

    // 3. Add to gesture history
    const historyEntry = {
        gesture: detection.gesture,
        distance: detection.distance,
        timestamp: sessionTime // Use session time for the timestamp
    };
    gestureHistory.unshift(historyEntry); // Add to the beginning

    // Limit history size
    if (gestureHistory.length > 50) {
        gestureHistory.pop();
    }

    // Optional: Trigger a UI update
    if (window.updateAllUI) {
        window.updateAllUI(getStats());
    }
}

// --- Getter Functions ---

/**
 * Returns the current state of all statistics.
 */
export function getStats() {
    return {
        totalDetections,
        sessionTime,
        averageDistance: calculateAverageDistance(),
        gestureHistory: [...gestureHistory] // Return a copy
    };
}

/**
 * Calculates the current average distance.
 * @returns {number | null} The average distance or null if no samples.
 */
function calculateAverageDistance() {
    if (distanceSamples === 0) {
        return null;
    }
    return Math.round(totalDistance / distanceSamples);
}

// --- Utility for UI ---

/**
 * Formats seconds into a MM:SS string.
 * @param {number} totalSeconds - The total seconds to format.
 * @returns {string} The formatted time string.
 */
export function formatTime(totalSeconds) {
    const minutes = Math.floor(totalSeconds / 60).toString().padStart(2, '0');
    const seconds = (totalSeconds % 60).toString().padStart(2, '0');
    return `${minutes}:${seconds}`;
}
