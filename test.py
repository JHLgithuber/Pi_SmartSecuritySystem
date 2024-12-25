from keras.models import load_model
import cv2
import numpy as np

# Disable scientific notation for clarity
np.set_printoptions(suppress=True)

# Load the deep learning model
model = load_model("/home/rpi5/teamproject/keras_model.h5", compile=False)

# Load class labels
class_names = open("/home/rpi5/teamproject/labels.txt", "r").readlines()

# Load Haar Cascade for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

# Activate webcam
camera = cv2.VideoCapture(0)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Frame rate settings
frame_rate = 5
prev = 0

while True:
    # Get the current time
    time_elapsed = cv2.getTickCount() / cv2.getTickFrequency()

    if time_elapsed - prev >= 1.0 / frame_rate:
        prev = time_elapsed

        # Capture an image from the webcam
        ret, frame = camera.read()

        if not ret:
            break

        # Image preprocessing
        resized_image = cv2.resize(frame, (224, 224), interpolation=cv2.INTER_AREA)
        normalized_image = np.asarray(resized_image, dtype=np.float32).reshape(1, 224, 224, 3)
        normalized_image = (normalized_image / 127.5) - 1

        # Predict using the model
        prediction = model.predict(normalized_image)
        index = np.argmax(prediction)
        class_name = class_names[index].strip()
        confidence_score = prediction[0][index]

        # Convert frame to grayscale and detect faces
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(50, 50))

        # Calculate object center and display information
        object_center_x = None
        display_info = False

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            object_center_x = x + w // 2  # Calculate object center
            display_info = True

        # Display information only if a face is detected
        if display_info:
            height, width, _ = frame.shape
            frame_center = width // 2
            direction = ""
            percentage_offset = 0.0

            if object_center_x < frame_center - width // 6:
                direction = "Left"
                distance_to_left = frame_center - object_center_x
                percentage_offset = (distance_to_left / frame_center) * 100
            elif object_center_x > frame_center + width // 6:
                direction = "Right"
                distance_to_right = object_center_x - frame_center
                percentage_offset = (distance_to_right / (width - frame_center)) * 100
            else:
                direction = "Center"
                percentage_offset = 0.0

            # Display the direction and percentage offset
            cv2.putText(frame, f"Direction: {direction}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, f"Offset: {percentage_offset:.2f}%", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # Print result in console
            print(f"Class: {class_name}, Confidence: {confidence_score * 100:.2f}%, Direction: {direction}, Offset: {percentage_offset:.2f}%")

        # Display the frame
        cv2.imshow("Webcam Image", frame)

    # Exit if 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
camera.release()
cv2.destroyAllWindows()
