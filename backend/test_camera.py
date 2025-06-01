import cv2

def test_camera():
    # Try multiple camera indices
    for index in range(3):  # Try indices 0, 1, and 2
        print(f"Trying camera index {index}")
        cap = cv2.VideoCapture(index)
        if cap.isOpened():
            # Read a frame to confirm it works
            ret, frame = cap.read()
            if ret:
                print(f"Successfully grabbed frame from camera at index {index}")
                # Save the frame to confirm camera works
                cv2.imwrite(f'camera_test_{index}.jpg', frame)
                print(f"Saved test image to camera_test_{index}.jpg")
            else:
                print(f"Could not grab frame from camera at index {index}")
            cap.release()
        else:
            print(f"Could not open camera at index {index}")

if __name__ == "__main__":
    test_camera()