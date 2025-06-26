// DOM Elements
const video = document.getElementById('webcam');
const canvas = document.getElementById('output');
const ctx = canvas.getContext('2d');
const startButton = document.getElementById('startCamera');
const stopButton = document.getElementById('stopCamera');
const exportButton = document.getElementById('exportLog');
const gestureOverlay = document.getElementById('gesture-overlay');
const distanceOverlay = document.getElementById('distance-overlay');
const gestureHistory = document.getElementById('gesture-history');
const totalDetections = document.getElementById('total-detections');
const currentGesture = document.getElementById('current-gesture');

// State
let stream = null;
let isProcessing = false;
let detectionCount = 0;
let lastGesture = null;

// Initialize Socket.IO
const socket = io();

// Event Listeners
startButton.addEventListener('click', startWebcam);
stopButton.addEventListener('click', stopWebcam);
exportButton.addEventListener('click', exportLog);

// Functions
async function startWebcam() {
    try {
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
        
        startButton.disabled = true;
        stopButton.disabled = false;
        
        // Start processing frames
        processVideo();
    } catch (err) {
        console.error('Error accessing webcam:', err);
        alert('Could not access the webcam. Please ensure you have granted camera permissions.');
    }
}

function stopWebcam() {
    if (stream) {
        const tracks = stream.getTracks();
        tracks.forEach(track => track.stop());
        stream = null;
        
        // Clear canvas
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        startButton.disabled = false;
        stopButton.disabled = true;
        
        // Reset UI
        gestureOverlay.textContent = 'No gesture detected';
        distanceOverlay.textContent = 'Distance: -- cm';
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

function updateUI(result) {
    // Update gesture overlay
    if (result.gesture && result.gesture !== lastGesture) {
        gestureOverlay.textContent = result.gesture;
        lastGesture = result.gesture;
        
        // Add to history
        addToHistory(result);
        
        // Update detection count
        detectionCount++;
        totalDetections.textContent = detectionCount;
    }
    
    // Update distance overlay
    if (result.distance) {
        distanceOverlay.textContent = `Distance: ${result.distance} cm`;
    }
    
    // Update current gesture
    if (result.gesture) {
        currentGesture.textContent = result.gesture;
    }
}

function addToHistory(result) {
    const now = new Date();
    const timeString = now.toLocaleTimeString();
    
    // Create history item
    const historyItem = document.createElement('div');
    historyItem.className = 'gesture-item p-3 rounded-lg flex justify-between items-center';
    historyItem.innerHTML = `
        <div class="flex items-center">
            <div class="w-10 h-10 rounded-full bg-yellow-500 bg-opacity-20 flex items-center justify-center mr-3">
                <i class="fas fa-hand-paper text-yellow-400"></i>
            </div>
            <div class="text-left">
                <p class="font-medium">${result.gesture}</p>
                <p class="text-xs text-gray-400">${timeString}</p>
            </div>
        </div>
        <div class="text-right">
            <p class="text-sm font-medium">${result.distance || '--'} cm</p>
        </div>
    `;
    
    // Insert at the top of history
    const firstItem = gestureHistory.firstChild;
    if (firstItem && firstItem.classList.contains('text-center')) {
        gestureHistory.removeChild(firstItem);
    }
    
    gestureHistory.insertBefore(historyItem, gestureHistory.firstChild);
    
    // Limit history items
    if (gestureHistory.children.length > 20) {
        gestureHistory.removeChild(gestureHistory.lastChild);
    }
}

function exportLog() {
    // Trigger download of gesture log
    window.location.href = '/export-log';
}

// Initialize UI
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
