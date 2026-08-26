import cv2
import numpy as np
from pathlib import Path
from database import get_all_students, mark_attendance


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

# -----------------------------
# Load students from sqlite
# -----------------------------

students = get_all_students()

if not students:
    print("No students registered in the database.")
    exit()

registered_students = []

for student_id, name, roll_no, embedding_bytes in students:

    # Convert bytes from SQLite back into a NumPy array
    embedding = np.frombuffer(
        embedding_bytes,
        dtype=np.float32
    ).reshape(1, -1)

    registered_students.append({
        "id": student_id,
        "name": name,
        "roll_no": roll_no,
        "embedding": embedding
    })

print(f"{len(registered_students)} students loaded.")

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

THRESHOLD = 0.363

while True:

    success, frame = camera.read()

    if not success:
        print("Error: Could not read camera frame.")
        break


    height, width = frame.shape[:2]

    detector.setInputSize((width, height))

    _, faces = detector.detect(frame)


    if faces is not None:

        for face in faces:

            x, y, w, h = face[:4].astype(int)


            # Align detected face
            aligned_face = recognizer.alignCrop(
                frame,
                face
            )


            # Generate SFace embedding
            feature = recognizer.feature(
                aligned_face
            )


            best_student = None
            best_score = -1


            # Compare with every registered student
            for student in registered_students:

                score = recognizer.match(
                    feature,
                    student["embedding"],
                    cv2.FaceRecognizerSF_FR_COSINE
                )

                if score > best_score:

                    best_score = score
                    best_student = student


            # ----------------------------
            # Recognized
            # ----------------------------

            if best_score >= THRESHOLD:

                name = best_student["name"]
                roll_no = best_student["roll_no"]
                student_id = best_student["id"]

                label = (
                    f"{name} - {roll_no} "
                    f"({best_score:.2f})"
                )

                marked = mark_attendance(student_id)

                if marked:
                    print(
                        f"Attendance marked: "
                        f"{name} ({roll_no})"
                    )


            # ----------------------------
            # Unknown
            # ----------------------------

            else:

                label = (
                    f"Unknown "
                    f"({best_score:.2f})"
                )


            # Draw face rectangle
            cv2.rectangle(
                frame,
                (x, y),
                (x + w, y + h),
                (0, 255, 0),
                2
            )


            # Display name/roll number
            cv2.putText(
                frame,
                label,
                (x, max(y - 10, 20)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )


    cv2.imshow(
        "Face Attendance",
        frame
    )


    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


camera.release()
cv2.destroyAllWindows()