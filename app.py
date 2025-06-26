from flask import Flask, render_template, Response, jsonify, request
from flask_socketio import SocketIO, emit
import cv2
import mediapipe as mp
import numpy as np
import os
from datetime import datetime
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(
    max_num_hands=2,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)

# Global variables to store gesture history
gesture_history = []
MAX_HISTORY = 50

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/detect', methods=['POST'])
def detect():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    
    file = request.files['image']
    img = cv2.imdecode(np.frombuffer(file.read(), np.uint8), cv2.IMREAD_COLOR)
    
    # Process the image with MediaPipe
    results = process_image(img)
    
    # Add to history
    if results and 'gesture' in results:
        gesture_history.append({
            'gesture': results['gesture'],
            'distance': results.get('distance', 0),
            'timestamp': datetime.now().isoformat()
        })
        # Keep only the last N entries
        if len(gesture_history) > MAX_HISTORY:
            gesture_history.pop(0)
    
    return jsonify(results)

def process_image(image):
    # Convert the BGR image to RGB and process it with MediaPipe
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(image_rgb)
    
    # Draw hand landmarks
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(
                image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            # Calculate hand distance (simplified)
            wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
            middle_finger_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP]
            distance = calculate_distance(wrist, middle_finger_mcp, image.shape)
            
            # Here you would add your gesture recognition logic
            gesture = detect_gesture(hand_landmarks)
            
            return {
                'gesture': gesture,
                'distance': distance,
                'hand_landmarks': [{'x': lm.x, 'y': lm.y, 'z': lm.z} 
                                 for lm in hand_landmarks.landmark]
            }
    return {}

def calculate_distance(wrist, mcp, image_shape):
    # Simple distance estimation based on hand size in the image
    # This is a simplified version - you might want to implement a more accurate method
    image_height, image_width = image_shape[:2]
    wrist_x, wrist_y = int(wrist.x * image_width), int(wrist.y * image_height)
    mcp_x, mcp_y = int(mcp.x * image_width), int(mcp.y * image_height)
    
    # Calculate distance in pixels
    distance_px = ((wrist_x - mcp_x) ** 2 + (wrist_y - mcp_y) ** 2) ** 0.5
    
    # Convert to cm (this is a rough estimation)
    # You would need to calibrate this based on your camera and typical hand sizes
    distance_cm = distance_px * 0.1  # Adjust this factor based on your needs
    
    return round(distance_cm, 1)

def detect_gesture(hand_landmarks):
    # This is a placeholder for your gesture recognition logic
    # You would implement a more sophisticated method here
    return "Gesture Detected"

@app.route('/export-log')
def export_log():
    # Convert gesture history to CSV
    csv_data = "timestamp,gesture,distance\n"
    for entry in gesture_history:
        csv_data += f"{entry['timestamp']},{entry['gesture']},{entry['distance']}\n"
    
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=gesture_log.csv"}
    )

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('logs', exist_ok=True)
    os.makedirs('static/images', exist_ok=True)
    
    # Run the app
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
