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
- **Deployment:** Docker, Render

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
    # Gunicorn in the Dockerfile uses $PORT.
    # For local testing, you can set this to any port, e.g., 5000 or 8080.
    docker run -p 5000:5000 -e PORT=5000 handsignvision
    ```
    The application will then be accessible at `http://localhost:5000`.
    Or, if you prefer to use port 8080 locally:
    ```bash
    docker run -p 8080:8080 -e PORT=8080 handsignvision
    ```
    And access it at `http://localhost:8080`. Render will provide its own `PORT` variable during deployment.

## Deployment to Render

This application can be deployed to [Render](https://render.com/) using its Git integration and Docker support. The `render.yaml` file in this repository can be used for "Blueprint" deployments.

**Steps to Deploy:**

1.  **Push your code to a GitHub (or GitLab) repository.**

2.  **On Render Dashboard:**
    *   Sign up or log in to Render.
    *   Click "New +" and select "Blueprint".
    *   Connect your GitHub/GitLab account and select the repository for this project.
    *   Render will detect the `render.yaml` file. Review the services it plans to create.
    *   Click "Approve" or "Create New Services".
    *   Alternatively, you can create a "New Web Service" manually:
        *   Connect your repository.
        *   Choose a unique name for your service.
        *   Set the Environment to "Docker".
        *   Select a region.
        *   Choose an instance type (e.g., "Free").
        *   Under "Advanced Settings", you might need to set a Health Check Path to `/health`.
        *   Click "Create Web Service".

3.  **Automatic Deployments:**
    *   Render can automatically build and deploy your application when you push changes to your connected repository branch (typically `main`).

4.  **Access Your Application:**
    *   Once deployed, Render will provide you with a public URL (e.g., `https://your-service-name.onrender.com`).

Refer to the `Dockerfile` and `render.yaml` for deployment configurations. Render injects a `PORT` environment variable which Gunicorn uses.

## Project Structure

```
.
├── static/               # Static files (CSS, JS)
│   ├── css/styles.css
│   └── js/main.js
├── templates/            # HTML templates (index.html)
├── app.py                # Main Flask application file
├── requirements.txt      # Python dependencies
├── Dockerfile            # Docker configuration for Render/local
├── render.yaml           # Render Blueprint configuration
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

- **Deployment Issues on Render:** Check the build and deployment logs in the Render dashboard for your service. Ensure system dependencies in the `Dockerfile` are correctly installed. Verify the Health Check Path is correctly set if not using `render.yaml`.
- **Local Docker Issues:** Ensure Docker Desktop (or your Docker environment) is running.
- **Free Tier Limitations on Render:** Free web services on Render spin down due to inactivity and may take some time to restart on a new request. They also have usage limits.

## License

This project is licensed under the MIT License. (Assuming MIT, update if different)

## Acknowledgments

- [MediaPipe](https://mediapipe.dev/) for hand tracking
- [Flask](https://flask.palletsprojects.com/) for the web framework
```
