import cv2
import numpy as np
from database import add_student
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


        # Convert the captured frame to JPEG bytes
        success, photo_buffer = cv2.imencode(".jpg", frame)

        if not success:
            print("Error: Could not encode photo.")
            continue

        photo_bytes = photo_buffer.tobytes()

        # Convert SFace embedding to bytes
        embedding_bytes = feature.astype(np.float32).tobytes()

        # Save student to SQLite
        saved = add_student(
            name,
            roll_no,
            photo_bytes,
            embedding_bytes
            )
        if saved:
            print("\nStudent registered successfully!")
            print(f"Name: {name}")
            print(f"Roll No: {roll_no}")
            break

    # Press Q to quit
    elif key == ord("q"):
        print("Registration cancelled.")
        break


camera.release()
cv2.destroyAllWindows()