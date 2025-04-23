import cv2
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
import joblib
from pathlib import Path

# Configuration (Modify these based on your dataset)
IMG_SIZE = 300  # Image size must match app.py
CLASSES = ["A", "B", "C", "D", "E"]  # Replace with your hand sign classes
SAMPLES_PER_CLASS = 50  # Number of training samples per class

def create_dummy_data():
    """Generates synthetic training data"""
    Path("assets").mkdir(exist_ok=True)
    
    X = []
    y = []
    
    # Create synthetic images (grayscale, 300x300)
    for class_idx, class_name in enumerate(CLASSES):
        for _ in range(SAMPLES_PER_CLASS):
            img = np.zeros((IMG_SIZE, IMG_SIZE))
            
            # Add class-specific features
            if class_name == "A":
                cv2.circle(img, (150,150), 100, 255, -1)
            elif class_name == "B":
                cv2.rectangle(img, (50,50), (250,250), 255, -1)
            # Add patterns for other classes...
            
            X.append(img.flatten())
            y.append(class_name)
    
    return np.array(X), np.array(y)

# Train and save the model
X_train, y_train = create_dummy_data()
model = KNeighborsClassifier(n_neighbors=3)
model.fit(X_train, y_train)

joblib.dump(model, "assets/model.pkl")
print(f"Model trained with {len(X_train)} samples")
print(f"Classes: {model.classes_}")
