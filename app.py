from flask import Flask, render_template, Response, jsonify, request
import cv2
import mediapipe as mp
import numpy as np
import os
import base64
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
            print("No image file in request")
            return jsonify({'error': 'No image provided'}), 400
        
        file = request.files['image']
        img_data = file.read()
        
        if not img_data:
            print("Received empty image data")
            return jsonify({'error': 'Empty image data'}), 400
            
        img = cv2.imdecode(np.frombuffer(img_data, np.uint8), cv2.IMREAD_COLOR)
        
        if img is None:
            print("Failed to decode image")
            return jsonify({'error': 'Failed to decode image'}), 400
            
        print(f"Processing image of size: {img.shape}")
        
        # Process the image with MediaPipe
        results = process_image(img)
        
        if 'error' in results:
            print(f"Error in process_image: {results['error']}")
            return jsonify({'error': results['error']}), 500
        
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
        
        # Prepare response
        response = {
            'gesture': results.get('gesture', 'No gesture'),
            'distance': results.get('distance', 0),
            'hand_landmarks': results.get('hand_landmarks', [])
        }
        
        # If we have a processed image, include it in the response
        if 'processed_image' in results:
            response['processed_image'] = results['processed_image']
            print(f"Sending response with processed image (size: {len(results['processed_image'])} chars)")
        else:
            print("No processed image in results")
        
        return jsonify(response)
        
    except Exception as e:
        print(f"Error in /detect endpoint: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

def process_image(image):
    try:
        # Create a copy of the original image for processing
        original_image = image.copy()
        
        # Convert the BGR image to RGB and process it with MediaPipe
        image_rgb = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)
        results = hands.process(image_rgb)
        
        # Create a black mask for the hand region
        mask = np.zeros(original_image.shape[:2], dtype=np.uint8)
        
        if results.multi_hand_landmarks:
            # Create a blank black image for drawing
            result = np.zeros_like(original_image)
            
            for hand_landmarks in results.multi_hand_landmarks:
                # Get hand landmarks as numpy array for easier processing
                h, w = original_image.shape[:2]
                landmarks = np.array([(int(lm.x * w), int(lm.y * h)) 
                                   for lm in hand_landmarks.landmark], dtype=np.int32)
                
                # Create a convex hull around the hand with padding
                hull = cv2.convexHull(landmarks)
                
                # Add padding to the convex hull
                padding = 30
                rect = cv2.boundingRect(hull)
                x, y, w, h = rect
                center = (x + w//2, y + h//2)
                
                # Create a larger mask for the hand region
                mask = np.zeros(original_image.shape[:2], dtype=np.uint8)
                cv2.drawContours(mask, [hull], -1, 255, -1)
                
                # Apply morphological operations to smooth the mask
                kernel = np.ones((15, 15), np.uint8)
                mask = cv2.dilate(mask, kernel, iterations=1)
                mask = cv2.GaussianBlur(mask, (25, 25), 0)
                
                # Create a 3-channel mask
                mask_3ch = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
                mask_3ch = mask_3ch.astype(float) / 255.0
                
                # Apply heavy blur to the original image
                kernel_size = max(51, min(original_image.shape[0], original_image.shape[1]) // 8 | 1)  # Ensure odd number
                blurred_bg = cv2.GaussianBlur(original_image, (kernel_size, kernel_size), 0)
                
                # Blend images using the mask
                result = (original_image * mask_3ch + blurred_bg * (1 - mask_3ch)).astype(np.uint8)
                
                # Draw hand skeleton with enhanced visualization
                mp_drawing.draw_landmarks(
                    result,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=4, circle_radius=6),  # Landmarks
                    mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=4)  # Connections
                )
                
                # Draw finger tips with numbers
                for idx, landmark in enumerate(hand_landmarks.landmark):
                    if idx in [4, 8, 12, 16, 20]:  # Fingertip landmarks
                        x, y = int(landmark.x * w), int(landmark.y * h)
                        cv2.circle(result, (x, y), 8, (0, 0, 255), -1)
                        cv2.putText(result, str(idx), (x - 5, y + 5),
                                 cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                
                # Calculate hand distance using the improved method
                distance = calculate_distance(hand_landmarks, image.shape)
                
                # Detect gesture
                gesture = detect_gesture(hand_landmarks)
                
                # Encode the result image as base64
                _, buffer = cv2.imencode('.jpg', cv2.cvtColor(result, cv2.COLOR_BGR2RGB), 
                                      [int(cv2.IMWRITE_JPEG_QUALITY), 90])
                processed_image = base64.b64encode(buffer).decode('utf-8')
                
                return {
                    'gesture': gesture,
                    'distance': distance,
                    'hand_landmarks': [{'x': lm.x, 'y': lm.y, 'z': lm.z} 
                                     for lm in hand_landmarks.landmark],
                    'processed_image': processed_image
                }
        
        # If no hands detected, return the blurred image
        blurred_bg = cv2.GaussianBlur(original_image, (99, 99), 0)
        _, buffer = cv2.imencode('.jpg', blurred_bg)
        processed_image = base64.b64encode(buffer).decode('utf-8')
        
        return {
            'gesture': 'No hand detected',
            'distance': 0,
            'hand_landmarks': [],
            'processed_image': processed_image
        }
        
    except Exception as e:
        print(f"Error in process_image: {str(e)}")
        return {'error': str(e)}

def calculate_distance(hand_landmarks, image_shape):
    """
    Calculate the distance from the camera to the hand using the hand's width.
    
    Args:
        hand_landmarks: MediaPipe hand landmarks
        image_shape: Shape of the image (height, width)
        
    Returns:
        Distance in centimeters
    """
    # Get the width of the hand (distance between wrist and middle finger MCP)
    wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
    mcp = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP]
    
    # Convert normalized coordinates to pixel values
    image_height, image_width = image_shape[:2]
    wrist_x, wrist_y = int(wrist.x * image_width), int(wrist.y * image_height)
    mcp_x, mcp_y = int(mcp.x * image_width), int(mcp.y * image_height)
    
    # Calculate hand width in pixels (Euclidean distance)
    hand_width_px = ((wrist_x - mcp_x) ** 2 + (wrist_y - mcp_y) ** 2) ** 0.5
    
    # Known average hand width in cm (from wrist to middle finger MCP)
    # This is an average value - you might need to adjust based on your hand size
    ACTUAL_HAND_WIDTH_CM = 8.0  # cm
    
    # Focal length estimation (you may need to calibrate this for your camera)
    # Formula: distance = (actual_width * focal_length) / width_in_pixels
    # For a typical webcam, focal length is approximately image_width * 1.2
    focal_length = image_width * 1.2
    
    # Calculate distance using the pinhole camera model
    if hand_width_px > 0:
        distance_cm = (ACTUAL_HAND_WIDTH_CM * focal_length) / hand_width_px
        # Apply smoothing and constraints
        distance_cm = max(10, min(100, distance_cm))  # Limit between 10cm and 100cm
        return round(distance_cm, 1)
    
    return 0

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
