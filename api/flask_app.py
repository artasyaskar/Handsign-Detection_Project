from flask import Flask, render_template, Response, jsonify, request
import cv2
import mediapipe as mp
import numpy as np
import os
from datetime import datetime
import json

# When deploying to Vercel, the Flask app instance must be named 'app'.
app = Flask(__name__)

# Initialize MediaPipe Hands
# Note: Vercel's serverless environment is stateless. 
# Initializing these here might lead to re-initialization on every request,
# which can be slow. Consider lazy loading or alternative approaches if performance is critical.
# For now, we keep it simple for compatibility.
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# It's important to initialize 'hands' once, if possible.
# However, in a serverless function, global state like this might not persist as expected
# or might be re-initialized frequently.
# For CPU-based tasks, this might be acceptable. For GPU, it's more problematic.
hands_instance = None

def get_hands_instance():
    global hands_instance
    if hands_instance is None:
        hands_instance = mp_hands.Hands(
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
    return hands_instance

# Global variables to store gesture history - This will NOT work as expected on Vercel.
# Serverless functions are stateless. Each request might be handled by a different instance.
# Gesture history needs to be stored in an external database or cache (e.g., Redis, Vercel KV).
# For this exercise, I will leave it but add a comment.
gesture_history = [] 
MAX_HISTORY = 50 # This limit will also be per-instance and not global.

@app.route('/')
def index():
    # Vercel typically serves static files from a root 'public' or 'static' directory
    # defined in vercel.json, not through Flask's render_template for the index.
    # However, to keep the Flask structure, we'll leave it, but this might need adjustment.
    # Ensure 'templates' and 'static' folders are correctly configured in vercel.json if served by Flask.
    # For Vercel, it's common to have a separate frontend or serve static HTML directly.
    return render_template('index.html')

@app.route('/detect', methods=['POST'])
def detect():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No image selected'}), 400
        
        img_data = file.read()
        img = cv2.imdecode(np.frombuffer(img_data, np.uint8), cv2.IMREAD_COLOR)
        
        if img is None:
            return jsonify({'error': 'Invalid image format'}), 400
        
        current_hands = get_hands_instance()
        results = process_image(img, current_hands)
        
        # Storing gesture_history in a global variable will not work reliably in a serverless environment.
        # Each invocation is stateless. This needs an external store.
        if results and 'gesture' in results and results['gesture'] != "No hand detected":
            gesture_history.append({
                'gesture': results['gesture'],
                'distance': results.get('distance', 0),
                'timestamp': datetime.now().isoformat()
            })
            if len(gesture_history) > MAX_HISTORY:
                gesture_history.pop(0)
        
        return jsonify(results)
    
    except Exception as e:
        # Log the exception for debugging on Vercel
        print(f"Error in /detect: {e}")
        return jsonify({'error': str(e)}), 500

def process_image(image, hands_detector):
    try:
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = hands_detector.process(image_rgb)
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Drawing on the image is not useful if we are just returning JSON.
                # If image output is needed, it should be encoded and sent.
                # mp_drawing.draw_landmarks(
                #     image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                
                wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
                middle_finger_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP]
                distance = calculate_distance(wrist, middle_finger_mcp, image.shape)
                
                gesture = detect_gesture(hand_landmarks)
                
                return {
                    'gesture': gesture,
                    'distance': distance,
                    'hand_landmarks': [{'x': lm.x, 'y': lm.y, 'z': lm.z} 
                                     for lm in hand_landmarks.landmark]
                }
        return {'gesture': 'No hand detected', 'distance': 0}
    
    except Exception as e:
        print(f"Error in process_image: {e}")
        return {'error': str(e)}

def calculate_distance(wrist, mcp, image_shape):
    try:
        image_height, image_width = image_shape[:2]
        wrist_x, wrist_y = int(wrist.x * image_width), int(wrist.y * image_height)
        mcp_x, mcp_y = int(mcp.x * image_width), int(mcp.y * image_height)
        
        distance_px = ((wrist_x - mcp_x) ** 2 + (wrist_y - mcp_y) ** 2) ** 0.5
        distance_cm = distance_px * 0.1 # Rough estimation
        
        return round(distance_cm, 1)
    except Exception as e:
        print(f"Error in calculate_distance: {e}")
        return 0

def detect_gesture(hand_landmarks):
    try:
        landmarks = hand_landmarks.landmark
        
        thumb_tip = landmarks[mp_hands.HandLandmark.THUMB_TIP]
        thumb_pip = landmarks[mp_hands.HandLandmark.THUMB_IP] # Corrected from THUMB_IP
        
        index_tip = landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP]
        index_pip = landmarks[mp_hands.HandLandmark.INDEX_FINGER_PIP]
        
        middle_tip = landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
        middle_pip = landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_PIP]
        
        ring_tip = landmarks[mp_hands.HandLandmark.RING_FINGER_TIP]
        ring_pip = landmarks[mp_hands.HandLandmark.RING_FINGER_PIP]
        
        pinky_tip = landmarks[mp_hands.HandLandmark.PINKY_TIP]
        pinky_pip = landmarks[mp_hands.HandLandmark.PINKY_PIP]
        
        fingers_up = []
        
        # Thumb: Compare x-coordinate for horizontal hand, y for vertical.
        # This simple logic might need adjustment based on hand orientation.
        # Assuming thumb is to the right (for a right hand) or left (for a left hand) of palm when extended.
        # A more robust way is to check distance from a palm center or wrist.
        if thumb_tip.x > landmarks[mp_hands.HandLandmark.THUMB_MCP].x : # Simplified
             fingers_up.append(1) # Thumb out
        else:
             fingers_up.append(0) # Thumb in
            
        for tip, pip in [(index_tip, index_pip), (middle_tip, middle_pip), 
                        (ring_tip, ring_pip), (pinky_tip, pinky_pip)]:
            if tip.y < pip.y: # Tip is above PIP (finger extended)
                fingers_up.append(1)
            else:
                fingers_up.append(0)
        
        total_fingers = sum(fingers_up)
        
        if total_fingers == 0:
            return "Fist"
        elif total_fingers == 1:
            if fingers_up[0] == 1: # Thumb is finger_up[0]
                 return "Thumbs Up"
            elif fingers_up[1] == 1: # Index finger
                return "Pointing"
            else:
                return "One Finger" 
        elif total_fingers == 2:
            if fingers_up[1] == 1 and fingers_up[2] == 1: # Index and Middle
                return "Peace Sign"
            else:
                return "Two Fingers"
        elif total_fingers == 5:
            return "Open Hand"
        else:
            return f"{total_fingers} Fingers"
            
    except Exception as e:
        print(f"Error in detect_gesture: {e}")
        return "Unknown Gesture"

@app.route('/export-log')
def export_log():
    # This will only export history from the current stateless instance, likely empty or very short.
    # Needs an external data store for meaningful export.
    try:
        csv_data = "timestamp,gesture,distance\n"
        for entry in gesture_history: # gesture_history will be instance-specific
            csv_data += f"{entry['timestamp']},{entry['gesture']},{entry['distance']}\n"
        
        return Response(
            csv_data,
            mimetype="text/csv",
            headers={"Content-disposition": "attachment; filename=gesture_log.csv"}
        )
    except Exception as e:
        print(f"Error in /export-log: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})

# The following block is for local execution (e.g., python api/flask_app.py)
# Vercel will use the 'app' instance directly and won't run this __main__ block.
if __name__ == '__main__':
    # Make sure to set the TEMPLATES_AUTO_RELOAD_DEFAULT to True for local dev if needed
    # app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5001)))
