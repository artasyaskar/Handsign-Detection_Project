# HandsignVision

An AI-powered web application for real-time hand gesture detection and distance estimation using computer vision. Upload images and see the results!

## Features

- Hand gesture detection from uploaded images using MediaPipe
- Hand distance estimation (simplified)
- Gesture history with timestamps for the current session
- Export gesture logs to CSV
- Clean and responsive user interface

## Core Technologies

- **Backend:** Python, Flask
- **Computer Vision:** OpenCV, MediaPipe
- **Frontend:** HTML, CSS, JavaScript
- **Deployment:** Docker, Railway

## Prerequisites for Local Development

- Python 3.9+
- pip (Python package manager)
- A modern web browser

## Local Development Setup

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd <your-repository-folder>
    ```

2.  **Create and activate a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: .\venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the Flask development server:**
    ```bash
    python app.py
    ```
    The application will be accessible at `http://127.0.0.1:5000`.

## Running with Docker Locally

This project includes a `Dockerfile` for containerized deployment.

1.  **Build the Docker image:**
    ```bash
    docker build -t handsignvision .
    ```

2.  **Run the Docker container:**
    ```bash
    # The application inside Docker will run on the port specified by the PORT env var (default 5000 in app.py)
    # We map port 5000 on the host to the container's application port.
    docker run -p 5000:5000 -e PORT=5000 handsignvision
    ```
    The application will be accessible at `http://localhost:5000`.
    *(Note: The `-e PORT=5000` is set to match how Gunicorn expects the port inside the container for local testing here. Railway will supply this automatically during deployment.)*

## Deployment to Railway

This application is configured for easy deployment to [Railway](https://railway.app/).

1.  **Push your code to a GitHub repository.**
2.  **On Railway:**
    *   Create a new project and connect it to your GitHub repository.
    *   Railway should automatically detect the `Dockerfile`.
    *   Railway will build the Docker image and deploy the application.
    *   A public URL will be provided to access your deployed application.
3.  **Environment Variables:**
    *   Railway automatically injects a `PORT` variable, which the application uses. No manual configuration of `PORT` is typically needed in Railway's settings for this project.

Refer to the `Dockerfile` and `railway.json` for deployment configurations.

## Project Structure

. ├── static/ # Static files (CSS, JS) │ ├── css/styles.css │ └── js/main.js ├── templates/ # HTML templates (index.html) ├── app.py # Main Flask application file ├── requirements.txt # Python dependencies ├── Dockerfile # Docker configuration for Railway/local ├── railway.json # Railway deployment configuration └── README.md # This file


## How it Works

1.  The user uploads an image through the web interface.
2.  The Flask backend receives the image.
3.  OpenCV and MediaPipe process the image to detect hand landmarks.
4.  A simple gesture recognition logic determines the gesture.
5.  Results (gesture, distance, landmarks) are sent back to the frontend and displayed.
6.  Detected gestures are logged and can be exported.

## Customization

### Gesture Logic

- Modify the `detect_gesture()` function in `app.py` to change or enhance gesture recognition.

### Styling

- Customize the look and feel by modifying `static/css/styles.css` and `templates/index.html`.

## Troubleshooting

- **Deployment Issues on Railway:** Check the build and deployment logs on Railway for any errors. Ensure system dependencies in the `Dockerfile` are correctly installed.
- **Local Docker Issues:** Ensure Docker Desktop (or your Docker environment) is running.
- **Python Dependencies:** If `pip install` fails, check for error messages; it might indicate missing system prerequisites for a package (though the `Dockerfile` aims to cover these for deployment).

