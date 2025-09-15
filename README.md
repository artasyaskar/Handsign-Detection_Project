# HandsignVision

An AI-powered web application for real-time hand gesture detection and distance estimation using computer vision.

## Features

- Real-time hand gesture detection using MediaPipe
- Hand distance estimation from the camera
- Gesture history with timestamps
- Export gesture logs to CSV
- Modern, responsive UI with dark theme
- WebRTC for browser-based camera access

## Prerequisites

- Python 3.8+
- pip (Python package manager)
- Modern web browser with WebRTC support (Chrome, Firefox, Edge)
- Webcam

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd Handsign_Detection.Project
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

### Development Mode

1. Start the Flask development server:
   ```bash
   python app.py
   ```

2. Open your web browser and navigate to:
   ```
   http://localhost:5000
   ```

### Using Docker

1. Build the Docker image:
   ```bash
   docker build -t handsignvision .
   ```

2. Run the container:
   ```bash
   docker run -p 5000:5000 --device=/dev/video0 handsignvision
   ```

3. Open your web browser and navigate to:
   ```
   http://localhost:5000
   ```

## Project Structure

```
HandsignVision/
├── static/               # Static files (CSS, JS, images)
│   ├── css/
│   └── js/
├── templates/            # HTML templates
├── app.py                # Main application file
├── requirements.txt      # Python dependencies
└── Dockerfile            # Docker configuration
```

## Usage

1. Click "Start Camera" to begin capturing video from your webcam.
2. Show your hand to the camera to detect gestures.
3. View detected gestures and hand distance in the interface.
4. Use the "Export Log" button to download a CSV of detected gestures.

## Customization

### Adding New Gestures

To add new gesture detection:

1. Modify the `detect_gesture()` function in `app.py` to recognize new hand landmarks patterns.
2. Add corresponding UI elements in `templates/index.html` if needed.

### Styling

Customize the look and feel by modifying the CSS in `static/css/styles.css`.

## Troubleshooting

- **Webcam not working**: Ensure you've granted camera permissions in your browser.
- **Installation issues**: Make sure all dependencies are installed correctly.
- **Performance issues**: Try reducing the video resolution in the code for better performance.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [MediaPipe](https://mediapipe.dev/) for hand tracking
- [Flask](https://flask.palletsprojects.com/) for the web framework
- [Tailwind CSS](https://tailwindcss.com/) for styling
