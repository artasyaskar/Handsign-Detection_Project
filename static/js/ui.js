// DOM Elements
const gestureOverlay = document.getElementById('gesture-overlay');
const distanceOverlay = document.getElementById('distance-overlay');
const gestureHistory = document.getElementById('gesture-history');

let lastGesture = null;

export function updateUI(result) {
    // Update gesture overlay
    if (result.gesture) {
        gestureOverlay.textContent = result.gesture;
    }
    
    // Update distance overlay
    if (result.distance) {
        distanceOverlay.textContent = `Distance: ${result.distance} cm`;
    }
    
    // Add to history if it's a new gesture or significant change
    if (result.gesture && result.gesture !== lastGesture) {
        addToHistory(result);
        lastGesture = result.gesture;
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

export function showStartingMessage() {
    gestureOverlay.textContent = 'Starting camera...';
}

export function showWebcamError() {
    gestureOverlay.textContent = 'Error: Could not access webcam.';
    alert('Could not access the webcam. Please ensure you have granted camera permissions and that no other application is using it.');
}

export function resetUI() {
    gestureOverlay.textContent = 'No gesture detected';
    distanceOverlay.textContent = 'Distance: -- cm';
}
