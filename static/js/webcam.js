import { updateUI, showStartingMessage, showWebcamError, resetUI } from './ui.js';

// DOM Elements
const video = document.getElementById('webcam');
const canvas = document.getElementById('output');
const ctx = canvas.getContext('2d');

// State
let stream = null;
let isProcessing = false;

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
        
        // Start processing frames
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
        
        // Clear canvas
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        resetUI();
    }
}

async function processVideo() {
    if (!stream || isProcessing) return;
    
    isProcessing = true;
    
    try {
        // Capture frame from video
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        
        // Get image data and send to server for processing
        const imageData = canvas.toDataURL('image/jpeg', 0.8);
        
        // Send to server via fetch API
        const formData = new FormData();
        const blob = await (await fetch(imageData)).blob();
        formData.append('image', blob, 'frame.jpg');
        
        const response = await fetch('/detect', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.gesture) {
            updateUI(result);
        }
    } catch (err) {
        console.error('Error processing frame:', err);
    }
    
    isProcessing = false;
    
    // Continue processing frames
    if (stream) {
        requestAnimationFrame(processVideo);
    }
}
