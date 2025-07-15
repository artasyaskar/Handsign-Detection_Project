import { formatTime } from './stats.js';

// DOM Elements
const gestureOverlay = document.getElementById('gesture-overlay');
const distanceOverlay = document.getElementById('distance-overlay');
const gestureHistoryEl = document.getElementById('gesture-history');
const totalDetectionsEl = document.getElementById('total-detections');
const sessionTimeEl = document.getElementById('session-time');
const avgDistanceEl = document.getElementById('avg-distance');

/**
 * Updates all UI elements with the latest detection result and stats.
 * @param {object} result - The detection result from the server.
 * @param {object} stats - The latest statistics from the stats module.
 */
export function updateUI(result, stats) {
    // Update gesture and distance overlays
    if (result.gesture) {
        gestureOverlay.textContent = result.gesture;
    }
    if (result.distance) {
        distanceOverlay.textContent = `Distance: ${result.distance} cm`;
    }

    // Update the statistics panel
    updateStatsUI(stats);

    // Update the gesture history panel
    updateGestureHistoryUI(stats.gestureHistory);
}

/**
 * Updates only the statistics panel.
 * @param {object} stats - The latest statistics.
 */
export function updateStatsUI(stats) {
    if (stats.totalDetections !== undefined) {
        totalDetectionsEl.textContent = stats.totalDetections;
    }
    if (stats.sessionTime !== undefined) {
        sessionTimeEl.textContent = formatTime(stats.sessionTime);
    }
    if (stats.averageDistance !== null && stats.averageDistance !== undefined) {
        avgDistanceEl.textContent = `${stats.averageDistance} cm`;
    } else {
        avgDistanceEl.textContent = '-- cm';
    }
}

/**
 * Updates the gesture history panel.
 * @param {Array} history - The gesture history array.
 */
function updateGestureHistoryUI(history) {
    gestureHistoryEl.innerHTML = ''; // Clear existing history

    if (history.length === 0) {
        gestureHistoryEl.innerHTML = `
            <div class="text-center text-gray-400 py-8">
                <i class="fas fa-history text-4xl mb-4 opacity-50"></i>
                <p>No gestures detected yet</p>
                <p class="text-sm">The history will appear here</p>
            </div>
        `;
        return;
    }

    for (const item of history) {
        const historyItem = document.createElement('div');
        historyItem.className = 'gesture-item p-3 rounded-lg flex justify-between items-center';
        historyItem.innerHTML = `
            <div class="flex items-center">
                <div class="w-10 h-10 rounded-full bg-yellow-500 bg-opacity-20 flex items-center justify-center mr-3">
                    <i class="fas fa-hand-paper text-yellow-400"></i>
                </div>
                <div class="text-left">
                    <p class="font-medium">${item.gesture}</p>
                    <p class="text-xs text-gray-400">${formatTime(item.timestamp)}</p>
                </div>
            </div>
            <div class="text-right">
                <p class="text-sm font-medium">${item.distance || '--'} cm</p>
            </div>
        `;
        gestureHistoryEl.appendChild(historyItem);
    }
}

/**
 * Resets the entire UI to its initial state.
 */
export function resetUI() {
    gestureOverlay.textContent = 'No gesture detected';
    distanceOverlay.textContent = 'Distance: -- cm';
    totalDetectionsEl.textContent = '0';
    sessionTimeEl.textContent = '00:00';
    avgDistanceEl.textContent = '-- cm';
    updateGestureHistoryUI([]); // Clear history panel
}

export function showStartingMessage() {
    gestureOverlay.textContent = 'Starting camera...';
    resetUI(); // Reset stats when starting
}

export function showWebcamError() {
    gestureOverlay.textContent = 'Error: Could not access webcam.';
    alert('Could not access the webcam. Please ensure you have granted camera permissions and that no other application is using it.');
}

// Expose a global function for the stats module to call for real-time updates
window.updateStatsUI = updateStatsUI;
