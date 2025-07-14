import { startWebcam, stopWebcam } from './webcam.js';

// DOM Elements
const startButton = document.getElementById('startCamera');
const stopButton = document.getElementById('stopCamera');
const exportButton = document.getElementById('exportLog');

// Event Listeners
startButton.addEventListener('click', async () => {
    const success = await startWebcam();
    if (success) {
        startButton.disabled = true;
        stopButton.disabled = false;
    }
});

stopButton.addEventListener('click', () => {
    stopWebcam();
    startButton.disabled = false;
    stopButton.disabled = true;
});

exportButton.addEventListener('click', () => {
    // Trigger download of gesture log
    window.location.href = '/export-log';
});

function init() {
    stopButton.disabled = true;
    
    // Check if browser supports mediaDevices
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        alert('Your browser does not support webcam access. Please try a modern browser like Chrome or Firefox.');
        startButton.disabled = true;
    }
}

// Initialize the app
init();
