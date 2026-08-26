import cv2
import numpy as np
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

DETECTION_MODEL = (
    BASE_DIR
    / "models"
    / "face_detection_yunet_2026may.onnx"
)

RECOGNITION_MODEL = (
    BASE_DIR
    / "models"
    / "face_recognition_sface_2021dec.onnx"
)

DATA_DIR = BASE_DIR / "registered_faces"
DATA_DIR.mkdir(exist_ok=True)


# Create YuNet detector
detector = cv2.FaceDetectorYN.create(
    str(DETECTION_MODEL),
    "",
    (320, 320),
    0.9,
    0.3,
    5000
)


# Create SFace recognizer
recognizer = cv2.FaceRecognizerSF.create(
    str(RECOGNITION_MODEL),
    ""
)


# Get student information
name = input("Enter student name: ")
roll_no = input("Enter roll number: ")

safe_roll_no = roll_no.replace("/", "_").replace(" ", "_")

photo_path = DATA_DIR / f"{safe_roll_no}.jpg"
embedding_path = DATA_DIR / f"{safe_roll_no}.npy"

# Check if this roll number already exists
if photo_path.exists() or embedding_path.exists():
    print(f"\nError: Roll number '{roll_no}' is already registered.")
    print("Registration cancelled.")
    exit()

    
# Open camera
camera = cv2.VideoCapture(1)

if not camera.isOpened():
    print("Error: Could not open camera.")
    exit()


print("\nCamera started.")
print("Press S to save your face.")
print("Press Q to quit.")


while True:
    success, frame = camera.read()

    if not success:
        print("Error: Could not read camera frame.")
        break

    height, width = frame.shape[:2]

    # Set YuNet input size to match camera frame
    detector.setInputSize((width, height))

    # Detect faces
    _, faces = detector.detect(frame)

    detected_face = None

    if faces is not None:

        # Use the first detected face
        detected_face = faces[0]

        x, y, w, h = detected_face[:4].astype(int)

        # Draw rectangle
        cv2.rectangle(
            frame,
            (x, y),
            (x + w, y + h),
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            "Face Detected - Press S to Save",
            (x, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0),
            2
        )

    else:

        cv2.putText(
            frame,
            "No Face Detected",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 0, 255),
            2
        )

    cv2.imshow("Register Student", frame)

    key = cv2.waitKey(1) & 0xFF

    # Press S to register
    if key == ord("s"):

        if detected_face is None:
            print("No face detected. Try again.")
            continue

        # Align and crop the face
        aligned_face = recognizer.alignCrop(
            frame,
            detected_face
        )

        # Generate SFace embedding
        feature = recognizer.feature(
            aligned_face
        )

        # Create safe filenames
        safe_roll_no = roll_no.replace("/", "_").replace(" ", "_")

        photo_path = DATA_DIR / f"{safe_roll_no}.jpg"
        embedding_path = DATA_DIR / f"{safe_roll_no}.npy"

        # Save original camera frame
        cv2.imwrite(
            str(photo_path),
            frame
        )

        # Save face embedding
        np.save(
            str(embedding_path),
            feature
        )

        print("\nStudent registered successfully!")
        print(f"Name: {name}")
        print(f"Roll No: {roll_no}")
        print(f"Photo saved: {photo_path}")
        print(f"Embedding saved: {embedding_path}")
        print(f"Embedding shape: {feature.shape}")

        break

    # Press Q to quit
    elif key == ord("q"):
        print("Registration cancelled.")
        break


camera.release()
cv2.destroyAllWindows()