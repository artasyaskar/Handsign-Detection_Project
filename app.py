import streamlit as st
import cv2
import numpy as np
import joblib
import os
from streamlit_webrtc import webrtc_streamer

# Define the model path
MODEL_PATH = 'assets/model.pkl'

# Load the pre-trained model
def load_model():
    # Debugging line to check the model file path
    st.write(f"Checking model file path: {MODEL_PATH}")
    if os.path.exists(MODEL_PATH):
        st.write("Model file found!")
        return joblib.load(MODEL_PATH)
    else:
        st.write("Model file NOT found!")
        raise FileNotFoundError(f"Model file not found at {MODEL_PATH}")

# Hand sign categories
CLASSES = ["A", "B", "C", "D", "E"]  # Adjust according to your model's classes

# Camera distance estimation function
def estimate_distance(hand_size):
    # Simple formula to estimate distance from camera based on hand size
    return max(0, 100 / (hand_size + 1))  # Adjust based on testing

# Hand sign detection function
def detect_sign(frame, model):
    # Convert the frame to grayscale and resize it to match the model's input
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    resized = cv2.resize(gray, (300, 300)).flatten()
    
    # Predict the sign
    prediction = model.predict([resized])
    return prediction[0], frame

# Streamlit video stream handler
def video_frame_callback(frame):
    # Convert the frame to a NumPy array
    img = frame.to_ndarray(format="bgr24")
    
    try:
        # Detect hand sign and get processed frame
        sign, processed_frame = detect_sign(img, model)
        
        # Estimate hand size (simplistic method)
        hand_size = np.sum(processed_frame > 128)  # Simplistic hand size calculation
        distance = estimate_distance(hand_size)
        
        # Display the results on Streamlit
        st.markdown(f"**Detected Sign**: {sign}")
        st.markdown(f"**Distance from Camera**: {distance:.2f} cm")
    except Exception as e:
        st.error(f"Error: {e}")
    
    # Return the frame to be displayed
    return frame

# Load model when the app starts
try:
    model = load_model()
except FileNotFoundError as e:
    st.error(f"Error loading model: {e}")

# Streamlit UI
def main():
    st.title("Real-Time Hand Sign Detection")
    
    # Start the WebRTC streamer for real-time video stream processing
    webrtc_streamer(key="example", video_frame_callback=video_frame_callback)

if __name__ == "__main__":
    main()
