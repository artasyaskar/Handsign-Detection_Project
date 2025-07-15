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
    landmarks = hand_landmarks.landmark

    # Landmark aliases
    thumb_tip = landmarks[mp_hands.HandLandmark.THUMB_TIP]
    thumb_mcp = landmarks[mp_hands.HandLandmark.THUMB_MCP]
    
    index_tip = landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    index_mcp = landmarks[mp_hands.HandLandmark.INDEX_FINGER_MCP]
    
    middle_tip = landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
    middle_mcp = landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_MCP]
    
    ring_tip = landmarks[mp_hands.HandLandmark.RING_FINGER_TIP]
    ring_mcp = landmarks[mp_hands.HandLandmark.RING_FINGER_MCP]
    
    pinky_tip = landmarks[mp_hands.HandLandmark.PINKY_TIP]
    pinky_mcp = landmarks[mp_hands.HandLandmark.PINKY_MCP]

    # Helper to check if a finger is extended
    def is_finger_open(tip, mcp):
        return tip.y < mcp.y

    # Gesture logic functions
    def is_open_palm():
        return all(is_finger_open(t, m) for t, m in [
            (thumb_tip, thumb_mcp),
            (index_tip, index_mcp),
            (middle_tip, middle_mcp),
            (ring_tip, ring_mcp),
            (pinky_tip, pinky_mcp)
        ])

    def is_fist():
        return all(not is_finger_open(t, m) for t, m in [
            (thumb_tip, thumb_mcp),
            (index_tip, index_mcp),
            (middle_tip, middle_mcp),
            (ring_tip, ring_mcp),
            (pinky_tip, pinky_mcp)
        ])

    def is_peace_sign():
        return (is_finger_open(index_tip, index_mcp) and
                is_finger_open(middle_tip, middle_mcp) and
                not is_finger_open(ring_tip, ring_mcp) and
                not is_finger_open(pinky_tip, pinky_mcp))

    def is_pointing():
        return (is_finger_open(index_tip, index_mcp) and
                not is_finger_open(middle_tip, middle_mcp) and
                not is_finger_open(ring_tip, ring_mcp) and
                not is_finger_open(pinky_tip, pinky_mcp))

    def is_thumb_up():
        return (thumb_tip.y < thumb_mcp.y and
                all(not is_finger_open(t, m) for t, m in [
                    (index_tip, index_mcp),
                    (middle_tip, middle_mcp),
                    (ring_tip, ring_mcp),
                    (pinky_tip, pinky_mcp)
                ]))

    def is_thumb_down():
        return (thumb_tip.y > thumb_mcp.y and
                all(not is_finger_open(t, m) for t, m in [
                    (index_tip, index_mcp),
                    (middle_tip, middle_mcp),
                    (ring_tip, ring_mcp),
                    (pinky_tip, pinky_mcp)
                ]))

    def is_call_me():
        return (is_finger_open(thumb_tip, thumb_mcp) and
                is_finger_open(pinky_tip, pinky_mcp) and
                all(not is_finger_open(t, m) for t, m in [
                    (index_tip, index_mcp),
                    (middle_tip, middle_mcp),
                    (ring_tip, ring_mcp)
                ]))

    def is_rock_sign():
        return (is_finger_open(index_tip, index_mcp) and
                is_finger_open(pinky_tip, pinky_mcp) and
                not is_finger_open(middle_tip, middle_mcp) and
                not is_finger_open(ring_tip, ring_mcp))

    def is_middle_finger():
        return (is_finger_open(middle_tip, middle_mcp) and
                not is_finger_open(index_tip, index_mcp) and
                not is_finger_open(ring_tip, ring_mcp) and
                not is_finger_open(pinky_tip, pinky_mcp))

    def is_ok_sign():
        dist_thumb_index = ((thumb_tip.x - index_tip.x)**2 + (thumb_tip.y - index_tip.y)**2)**0.5
        return dist_thumb_index < 0.05 and all(
            is_finger_open(t, m) for t, m in [
                (middle_tip, middle_mcp),
                (ring_tip, ring_mcp),
                (pinky_tip, pinky_mcp)
            ])

    def is_fingers_crossed():
        return (is_finger_open(index_tip, index_mcp) and
                is_finger_open(middle_tip, middle_mcp) and
                abs(index_tip.x - middle_tip.x) < 0.02)

    def is_i_love_you():
        return (is_finger_open(thumb_tip, thumb_mcp) and
                is_finger_open(index_tip, index_mcp) and
                not is_finger_open(middle_tip, middle_mcp) and
                not is_finger_open(ring_tip, ring_mcp) and
                is_finger_open(pinky_tip, pinky_mcp))

    # Matching known gestures
    if is_open_palm(): return "🖐️ Open Hand"
    if is_fist(): return "✊ Fist"
    if is_peace_sign(): return "✌️ Peace"
    if is_pointing(): return "👉 Pointing"
    if is_thumb_up(): return "👍 Thumbs Up"
    if is_thumb_down(): return "👎 Thumbs Down"
    if is_call_me(): return "🤙 Call Me"
    if is_rock_sign(): return "🤘 Rock"
    if is_middle_finger(): return "🖕Fuck You"
    if is_ok_sign(): return "👌 OK Sign"
    if is_fingers_crossed(): return "🤞 Fingers Crossed"
    if is_i_love_you(): return "🤟 I Love You"

    if (is_finger_open(middle_tip, middle_mcp) and
        not is_finger_open(index_tip, index_mcp) and
        not is_finger_open(ring_tip, ring_mcp) and
        not is_finger_open(pinky_tip, pinky_mcp)):
        return "🖕Fuck You"

    return "🤷 Gesture Detected"


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
    # Run the app for local development
    # Vercel will use a WSGI server and not this block
    app.run(debug=True, host='0.0.0.0', port=5000)
