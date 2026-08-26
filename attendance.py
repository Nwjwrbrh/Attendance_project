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


# -----------------------------
# Load registered face features
# -----------------------------

registered_faces = {}

for embedding_file in DATA_DIR.glob("*.npy"):

    roll_no = embedding_file.stem

    feature = np.load(embedding_file)

    registered_faces[roll_no] = feature


if not registered_faces:
    print("No registered faces found.")
    print("Please register a student first.")
    exit()


print("Registered students:")

for roll_no in registered_faces:
    print("-", roll_no)


# -----------------------------
# Create YuNet detector
# -----------------------------

detector = cv2.FaceDetectorYN.create(
    str(DETECTION_MODEL),
    "",
    (320, 320),
    0.9,
    0.3,
    5000
)


# -----------------------------
# Create SFace recognizer
# -----------------------------

recognizer = cv2.FaceRecognizerSF.create(
    str(RECOGNITION_MODEL),
    ""
)


# -----------------------------
# Open camera
# -----------------------------

camera = cv2.VideoCapture(1)

if not camera.isOpened():
    print("Error: Could not open camera.")
    exit()


print("\nAttendance recognition started.")
print("Press Q to quit.")


# -----------------------------
# Recognition loop
# -----------------------------

while True:

    success, frame = camera.read()

    if not success:
        print("Error: Could not read camera frame.")
        break


    height, width = frame.shape[:2]


    # Update YuNet input size
    detector.setInputSize((width, height))


    # Detect faces
    _, faces = detector.detect(frame)


    if faces is not None:

        for face in faces:

            # Get face rectangle
            x, y, w, h = face[:4].astype(int)


            # Align the face
            aligned_face = recognizer.alignCrop(
                frame,
                face
            )


            # Generate face feature
            feature = recognizer.feature(
                aligned_face
            )


            # Variables for the best match
            best_match = "Unknown"
            best_score = -1


            # Compare with every registered face
            for roll_no, registered_feature in registered_faces.items():

                score = recognizer.match(
                    feature,
                    registered_feature,
                    cv2.FaceRecognizerSF_FR_COSINE
                )


                if score > best_score:

                    best_score = score
                    best_match = roll_no


            # Recognition threshold
            # You can adjust this later
            THRESHOLD = 0.363


            if best_score >= THRESHOLD:

                label = f"{best_match} ({best_score:.2f})"

            else:

                label = f"Unknown ({best_score:.2f})"


            # Draw face rectangle
            cv2.rectangle(
                frame,
                (x, y),
                (x + w, y + h),
                (0, 255, 0),
                2
            )


            # Display result
            cv2.putText(
                frame,
                label,
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )


    # Show camera
    cv2.imshow(
        "Face Attendance",
        frame
    )


    # Press Q to quit
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


# Release camera
camera.release()

cv2.destroyAllWindows()