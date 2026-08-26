import cv2

MODEL_PATH = "models/face_detection_yunet_2026may.onnx"

detector = cv2.FaceDetectorYN.create(
    MODEL_PATH,
    "",
    (320,320),
    0.9,
    0.3,
    5000
)

camera = cv2.VideoCapture(1)

if not camera.isOpened():
    print("Error: Could not open camera.")
    exit()

print("Face detection started.")
print("Press Q to quit")

while True:
    success, frame = camera.read()

    if not success:
        print("Error: Could not read frame.")
        break

    height, width = frame.shape[:2]

    detector.setInputSize((width, height))

    _, faces = detector.detect(frame)

    if faces is not None:

        for face in faces:
            x, y, w, h = face[:4].astype(int)

            cv2.rectangle(
                frame,
                (x,y),
                (x + w, y + h ),
                (0, 255, 0),
                2
            )
    cv2.imshow("Yunet Face Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()