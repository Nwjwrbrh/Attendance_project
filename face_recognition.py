import cv2
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

detector = cv2.FaceDetectorYN.create(
    str(DETECTION_MODEL),
    "",
    (320, 320),
    0.9,
    0.3,
    5000
)

recognizer = cv2.FaceRecognizerSF.create(
    str(RECOGNITION_MODEL),
    ""
)

camera = cv2.VideoCapture(1)

if not camera.isOpened():
    print("Error: Could not open camera.")
    exit()

print("SFace feature extraction started.")
print("Press Q to quit.")

while True:
    success, frame = camera.read()

    if not success:
        print("Could not read camera frame.")
        break

    height, width = frame.shape[:2]

    detector.setInputSize((width, height))

    _, faces = detector.detect(frame)

    if faces is not None:

        for face in faces:

            x, y, w, h = face[:4].astype(int)

            cv2.rectangle(
                frame,
                (x, y),
                (x + w, y + h),
                (0, 255, 0),
                2
            )

            aligned_face = recognizer.alignCrop(
                frame,
                face
            )

            feature = recognizer.feature(
                aligned_face
            )

            cv2.putText(
                frame,
                f"Feature size: {feature.shape[1]}",
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )

            print(feature.shape)

    cv2.imshow("SFace Feature Extraction", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


camera.release()
cv2.destroyAllWindows()