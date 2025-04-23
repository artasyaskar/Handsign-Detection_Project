import cv2
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
import joblib
from pathlib import Path

# Configuration
IMG_SIZE = 300
CLASSES = [
    "peace", "fist", "thumbs_up", "stop", "ok",
    "call_me", "victory", "rock_on", "open_hand", "closed_hand"
]
SAMPLES_PER_CLASS = 50

def create_dummy_data():
    Path("assets").mkdir(exist_ok=True)

    X, y = []

    for idx, class_name in enumerate(CLASSES):
        for _ in range(SAMPLES_PER_CLASS):
            img = np.zeros((IMG_SIZE, IMG_SIZE), dtype=np.uint8)

            # Add visual patterns for each gesture class
            if class_name == "peace":
                cv2.line(img, (100, 100), (200, 200), 255, 8)
                cv2.line(img, (100, 200), (200, 100), 255, 8)
            elif class_name == "fist":
                cv2.rectangle(img, (100, 100), (200, 200), 255, -1)
            elif class_name == "thumbs_up":
                cv2.arrowedLine(img, (150, 200), (150, 100), 255, 10)
            elif class_name == "stop":
                cv2.putText(img, "STOP", (60, 160), cv2.FONT_HERSHEY_SIMPLEX, 2, 255, 5)
            elif class_name == "ok":
                cv2.circle(img, (150, 150), 50, 255, 8)
            elif class_name == "call_me":
                cv2.putText(img, "🤙", (110, 180), cv2.FONT_HERSHEY_SIMPLEX, 2, 255, 5)
            elif class_name == "victory":
                cv2.putText(img, "✌️", (110, 180), cv2.FONT_HERSHEY_SIMPLEX, 2, 255, 5)
            elif class_name == "rock_on":
                cv2.putText(img, "🤘", (110, 180), cv2.FONT_HERSHEY_SIMPLEX, 2, 255, 5)
            elif class_name == "open_hand":
                cv2.putText(img, "🖐️", (110, 180), cv2.FONT_HERSHEY_SIMPLEX, 2, 255, 5)
            elif class_name == "closed_hand":
                cv2.putText(img, "✊", (110, 180), cv2.FONT_HERSHEY_SIMPLEX, 2, 255, 5)

            X.append(img.flatten())
            y.append(class_name)

    return np.array(X), np.array(y)

# Train and export model
X_train, y_train = create_dummy_data()
model = KNeighborsClassifier(n_neighbors=3)
model.fit(X_train, y_train)

joblib.dump(model, "assets/model.pkl")
print(f"✅ Model trained on {len(CLASSES)} classes with {len(X_train)} samples")
print(f"Saved to: assets/model.pkl")

