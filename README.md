# HandsignVision

An AI-powered web application for hand gesture detection from uploaded images using computer vision.

## Features

- Hand gesture detection from uploaded images using MediaPipe
- Simplified hand distance estimation from image analysis
- Gesture history with timestamps for the current session
- Export gesture logs to CSV
- Clean and responsive user interface

## Core Technologies

- **Backend:** Python, Flask
- **Computer Vision:** OpenCV, MediaPipe
- **Frontend:** HTML, CSS, JavaScript
- **Deployment:** Docker, Fly.io

## Prerequisites for Local Development

- Python 3.9+ (as per Dockerfile)
- pip (Python package manager)
- A modern web browser

## Local Development Setup

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd <your-repository-folder-name> # e.g., HandsignVision
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
    # The application inside Docker will listen on the port specified by the PORT env var.
    # Gunicorn in the Dockerfile uses $PORT, which defaults to 5000 in app.py if not set.
    # For local testing to mimic Fly.io's typical internal port, you can use 8080:
    docker run -p 8080:8080 -e PORT=8080 handsignvision
    ```
    The application will then be accessible at `http://localhost:8080`.
    If you prefer to use port 5000 locally:
    ```bash
    docker run -p 5000:5000 -e PORT=5000 handsignvision
    ```
    And access it at `http://localhost:5000`.

## Deployment to Fly.io

This application is configured for deployment to [Fly.io](https://fly.io/) using its `flyctl` command-line tool.

1.  **Install `flyctl`:**
    Follow the instructions on the [Fly.io website](https://fly.io/docs/hands-on/install-flyctl/).

2.  **Log in to Fly.io:**
    ```bash
    flyctl auth login
    ```

3.  **Launch the app (first-time deployment):**
    Navigate to your project directory in the terminal and run:
    ```bash
    flyctl launch
    ```
    This command will:
    *   Prompt you to choose an application name (e.g., `handsignvision-app` or your own unique name). This will update the `app` field in `fly.toml`.
    *   Ask you to select an organization and a primary region for deployment.
    *   Detect the `Dockerfile` and `fly.toml`. It might ask if you want to copy the existing `fly.toml` settings.
    *   Optionally, it can provision a PostgreSQL database (select "No" if not needed for this app) and set up a Redis database (select "No").
    *   It will then attempt the first deployment.

4.  **Deploy Changes:**
    After the initial launch, to deploy subsequent changes you've pushed to your repository:
    ```bash
    flyctl deploy
    ```

5.  **Access Your Application:**
    Once deployed, `flyctl status` or `flyctl open` will show you the public URL of your application (e.g., `https://your-app-name.fly.dev`).

Refer to the `Dockerfile` and `fly.toml` for deployment configurations. The `fly.toml` file specifies health checks and how HTTP/HTTPS traffic is handled.

## Project Structure

```
.
├── static/               # Static files (CSS, JS)
│   ├── css/styles.css
│   └── js/main.js
├── templates/            # HTML templates (index.html)
├── app.py                # Main Flask application file
├── requirements.txt      # Python dependencies
├── Dockerfile            # Docker configuration for Fly.io/local
├── fly.toml              # Fly.io deployment configuration
└── README.md             # This file
```

## How it Works (Image Upload Version)

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

- **Deployment Issues on Fly.io:** Check the build logs using `flyctl logs` or in the Fly.io dashboard. Ensure system dependencies in the `Dockerfile` are correctly installed. The `fly.toml` health checks also provide insights into app health.
- **Local Docker Issues:** Ensure Docker Desktop (or your Docker environment) is running.
- **`flyctl launch` issues:** If `flyctl launch` has trouble detecting settings, ensure `fly.toml` is present or allow `flyctl` to generate a new one and then compare/merge if necessary.

## License

This project is licensed under the MIT License. (Assuming MIT, update if different)

## Acknowledgments

- [MediaPipe](https://mediapipe.dev/) for hand tracking
- [Flask](https://flask.palletsprojects.com/) for the web framework
```
