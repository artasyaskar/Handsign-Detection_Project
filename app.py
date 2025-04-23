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
    st.write(f"Checking model file path: {MODEL_PATH}")
    if os.path.exists(MODEL_PATH):
        st.success("✅ Model file found.")
        return joblib.load(MODEL_PATH)
    else:
        st.error("❌ Model file NOT found!")
        raise FileNotFoundError(f"Model file not found at {MODEL_PATH}")

# Inject custom JavaScript (script.js)
def local_js(js_file):
    if os.path.exists(js_file):
        with open(js_file) as f:
            st.markdown(f"<script>{f.read()}</script>", unsafe_allow_html=True)
    else:
        st.warning(f"⚠️ JavaScript file not found: {js_file}")

# Define hand sign classes
CLASSES = ["peace", "fist", "thumbs_up", "stop", "ok"]


# Estimate distance from camera based on hand area (very basic estimate)
def estimate_distance(hand_size):
    return max(0, 100 / (hand_size + 1))  # Adjust this logic based on testing

# Prediction logic
def detect_sign(frame, model):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    resized = cv2.resize(gray, (300, 300)).flatten()
    prediction = model.predict([resized])
    return prediction[0], frame

# Streamlit's WebRTC callback
def video_frame_callback(frame):
    img = frame.to_ndarray(format="bgr24")

    try:
        sign, processed_frame = detect_sign(img, model)
        hand_size = np.sum(processed_frame > 128)
        distance = estimate_distance(hand_size)

        # Show result
        st.markdown(f"<h4>Detected Sign: <span style='color:#00ffe4'>{sign}</span></h4>", unsafe_allow_html=True)
        st.markdown(f"<h4>Distance from Camera: <span id='distance-value'>{distance:.2f}</span> cm</h4>", unsafe_allow_html=True)
    except Exception as e:
        st.error(f"❌ Error: {e}")

    return frame

# App layout
def main():
    st.set_page_config(page_title="Handsign Detection", layout="centered")
    st.title("🖐️ Real-Time Hand Sign Detection")
    st.markdown("This app detects hand signs from your webcam and estimates how far your hand is from the camera.")

    # Run video stream
    webrtc_streamer(key="example", video_frame_callback=video_frame_callback)

    # Load custom JS
    local_js("static/js/script.js")

# Load model at startup
try:
    model = load_model()
except FileNotFoundError as e:
    st.error(f"Failed to load model: {e}")
    model = None

# Launch the app
if __name__ == "__main__":
    main()
