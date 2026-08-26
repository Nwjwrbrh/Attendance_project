import cv2

camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("Error: Could not open camera")
    exit()

print("camera started")
print("press Q to quit")

while True:
    success, frame = camera.read()
    if not success:
        print("Error: Could not read frame")
        break
    cv2.imshow("Camera test", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camera.release()

cv2.destroyAllWindows()