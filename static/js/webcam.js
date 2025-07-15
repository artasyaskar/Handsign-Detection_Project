import { updateUI, showStartingMessage, showWebcamError, resetUI } from './ui.js';
import { startSession, stopSession, recordDetection, getStats } from './stats.js';

// DOM Elements
const video = document.getElementById('webcam');
const canvas = document.getElementById('output');
const ctx = canvas.getContext('2d');

// State
let stream = null;
let isProcessing = false;
let animationFrameId = null;

export async function startWebcam() {
    try {
        showStartingMessage();
        stream = await navigator.mediaDevices.getUserMedia({
            video: {
                width: { ideal: 1280 },
                height: { ideal: 720 },
                facingMode: 'user'
            },
            audio: false
        });
        
        video.srcObject = stream;
        await video.play();
        
        // Set canvas size to match video
        video.onloadedmetadata = () => {
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
        };
        
        // Start statistics session
        startSession();

        // Start processing frames
        if (animationFrameId) {
            cancelAnimationFrame(animationFrameId);
        }
        processVideo();

        return true;
    } catch (err) {
        console.error('Error accessing webcam:', err);
        showWebcamError();
        return false;
    }
}

export function stopWebcam() {
    if (stream) {
        const tracks = stream.getTracks();
        tracks.forEach(track => track.stop());
        stream = null;
    }

    if (animationFrameId) {
        cancelAnimationFrame(animationFrameId);
        animationFrameId = null;
    }

    // Stop statistics session
    stopSession();

    // Clear canvas and reset UI
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    resetUI();
}

async function processVideo() {
    if (!stream) return;
    
    // Process the frame
    try {
        // Draw video to canvas
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        
        // Don't send a new request if the previous one is still processing
        if (isProcessing) {
            animationFrameId = requestAnimationFrame(processVideo);
            return;
        }

        isProcessing = true;

        // Get image data and send to server for processing
        const imageData = canvas.toDataURL('image/jpeg', 0.8);
        const blob = await (await fetch(imageData)).blob();
        const formData = new FormData();
        formData.append('image', blob, 'frame.jpg');
        
        const response = await fetch('/detect', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        // If a gesture is detected, record and update UI
        if (result && result.gesture) {
            recordDetection(result);
            updateUI(result, getStats());
        }

    } catch (err) {
        console.error('Error processing frame:', err);
    } finally {
        isProcessing = false;
    }
    
    // Continue processing frames
    animationFrameId = requestAnimationFrame(processVideo);
}

// A global function to update all UI components based on the latest stats
// This can be triggered from the stats module or other places if needed
window.updateAllUI = (stats) => {
    updateUI({}, stats); // Pass empty result as we only update stats
};
