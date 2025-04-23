import numpy as np
import cv2
from sklearn.neighbors import KNeighborsClassifier
import joblib
from pathlib import Path

# Configuration
IMG_SIZE = 300
CLASSES = ["peace", "fist", "thumbs_up", "stop", "ok"]
SAMPLES_PER_CLASS = 50

def create_dummy_data():
    Path("assets").mkdir(exist_ok=True)
    X, y = [], []

    for class_name in CLASSES:
        for _ in range(SAMPLES_PER_CLASS):
            img = np.random.randint(0, 256, (IMG_SIZE, IMG_SIZE), dtype=np.uint8)
            X.append(img.flatten())
            y.append(class_name)
    return np.array(X), np.array(y)

X_train, y_train = create_dummy_data()
model = KNeighborsClassifier(n_neighbors=3)
model.fit(X_train, y_train)
joblib.dump(model, "assets/model.pkl")
print("✅ Model saved to assets/model.pkl")


