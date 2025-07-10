from flask import Flask, render_template, Response, jsonify, request
import cv2
import mediapipe as mp
import numpy as np
import os
from datetime import datetime
import json

app = Flask(__name__)

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
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No image selected'}), 400
        
        # Read and decode the image
        img_data = file.read()
        img = cv2.imdecode(np.frombuffer(img_data, np.uint8), cv2.IMREAD_COLOR)
        
        if img is None:
            return jsonify({'error': 'Invalid image format'}), 400
        
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
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def process_image(image):
    try:
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
        return {'gesture': 'No hand detected', 'distance': 0}
    
    except Exception as e:
        return {'error': str(e)}

def calculate_distance(wrist, mcp, image_shape):
    try:
        # Simple distance estimation based on hand size in the image
        image_height, image_width = image_shape[:2]
        wrist_x, wrist_y = int(wrist.x * image_width), int(wrist.y * image_height)
        mcp_x, mcp_y = int(mcp.x * image_width), int(mcp.y * image_height)
        
        # Calculate distance in pixels
        distance_px = ((wrist_x - mcp_x) ** 2 + (wrist_y - mcp_y) ** 2) ** 0.5
        
        # Convert to cm (this is a rough estimation)
        distance_cm = distance_px * 0.1
        
        return round(distance_cm, 1)
    except:
        return 0

def detect_gesture(hand_landmarks):
    try:
        # Simple gesture recognition based on finger positions
        landmarks = hand_landmarks.landmark
        
        # Get finger tip and pip positions
        thumb_tip = landmarks[mp_hands.HandLandmark.THUMB_TIP]
        thumb_pip = landmarks[mp_hands.HandLandmark.THUMB_IP]
        
        index_tip = landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP]
        index_pip = landmarks[mp_hands.HandLandmark.INDEX_FINGER_PIP]
        
        middle_tip = landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
        middle_pip = landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_PIP]
        
        ring_tip = landmarks[mp_hands.HandLandmark.RING_FINGER_TIP]
        ring_pip = landmarks[mp_hands.HandLandmark.RING_FINGER_PIP]
        
        pinky_tip = landmarks[mp_hands.HandLandmark.PINKY_TIP]
        pinky_pip = landmarks[mp_hands.HandLandmark.PINKY_PIP]
        
        # Check if fingers are extended
        fingers_up = []
        
        # Thumb
        if thumb_tip.x > thumb_pip.x:
            fingers_up.append(1)
        else:
            fingers_up.append(0)
            
        # Other fingers
        for tip, pip in [(index_tip, index_pip), (middle_tip, middle_pip), 
                        (ring_tip, ring_pip), (pinky_tip, pinky_pip)]:
            if tip.y < pip.y:
                fingers_up.append(1)
            else:
                fingers_up.append(0)
        
        # Gesture recognition
        total_fingers = sum(fingers_up)
        
        if total_fingers == 0:
            return "Fist"
        elif total_fingers == 1:
            if fingers_up[1] == 1:
                return "Pointing"
            elif fingers_up[0] == 1:
                return "Thumbs Up"
            else:
                return "One Finger"
        elif total_fingers == 2:
            if fingers_up[1] == 1 and fingers_up[2] == 1:
                return "Peace Sign"
            else:
                return "Two Fingers"
        elif total_fingers == 5:
            return "Open Hand"
        else:
            return f"{total_fingers} Fingers"
            
    except Exception as e:
        return "Unknown Gesture"

@app.route('/export-log')
def export_log():
    try:
        # Convert gesture history to CSV
        csv_data = "timestamp,gesture,distance\n"
        for entry in gesture_history:
            csv_data += f"{entry['timestamp']},{entry['gesture']},{entry['distance']}\n"
        
        return Response(
            csv_data,
            mimetype="text/csv",
            headers={"Content-disposition": "attachment; filename=gesture_log.csv"}
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})

# For Vercel deployment
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
