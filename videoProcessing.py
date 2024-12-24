# videoProcessing.py
import cv2
import numpy as np
from keras.models import load_model
from time import sleep
import time

def run_video_processing(shared_dict, event_queue, gpio_queue, live_stream_queue):
    """
    라즈베리 파이 내부에서 카메라 영상을 읽어 모델 추론 후,
    결과 프레임을 JPEG 인코딩하여 live_stream_queue에 넣는 함수.
    """

    frame_queue = live_stream_queue
    print("Video Process start")

    # 과도한 지수 표기 방지
    np.set_printoptions(suppress=True)

    # 모델 로드
    model = load_model("/home/rpi5/teamproject/keras_model.h5", compile=False)

    # 클래스 라벨 로드
    class_names = open("/home/rpi5/teamproject/labels.txt", "r").readlines()

    # 얼굴인식용 Haar Cascade 로드
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )

    # 카메라 열기 (USB 웹캠이면 0, CSI 카메라이면 /dev/video0 등 환경에 맞게 변경)
    camera = cv2.VideoCapture(0)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    # (1) 카메라 정상 열렸는지 체크
    if not camera.isOpened():
        print("[ERROR] 카메라가 열리지 않았습니다. VideoProcessing 프로세스를 종료합니다.")
        return  # 프로세스 종료

    # 프레임레이트 제한
    frame_rate = 5
    prev = 0

    while True:
        time_elapsed = cv2.getTickCount() / cv2.getTickFrequency()

        # 지정한 frame_rate(초당 5프레임)로 제한
        if time_elapsed - prev >= 1.0 / frame_rate:
            prev = time_elapsed

            ret, frame = camera.read()

            # (2) 프레임 읽기 실패 시 예외 처리
            if not ret or frame is None:
                print("[WARNING] 카메라 프레임을 읽어오지 못했습니다. 잠시 후 재시도합니다.")
                sleep(0.1)
                continue

            # 이미지 전처리 (224x224, -1~1 범위로 정규화)
            resized_image = cv2.resize(frame, (224, 224), interpolation=cv2.INTER_AREA)
            normalized_image = np.asarray(resized_image, dtype=np.float32).reshape(
                1, 224, 224, 3
            )
            normalized_image = (normalized_image / 127.5) - 1

            # 모델 예측
            prediction = model.predict(normalized_image)
            index = np.argmax(prediction)
            class_name = class_names[index].strip()
            confidence_score = prediction[0][index]

            # 얼굴인식
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(
                gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(50, 50)
            )

            display_info = False
            object_center_x = None

            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                object_center_x = x + w // 2
                display_info = True

            # 얼굴이 검출된 경우에만 정보 표시
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

                # 콘솔 출력
                print(
                    f"Class: {class_name}, Confidence: {confidence_score * 100:.2f}%, "
                    f"Direction: {direction}, Offset: {percentage_offset:.2f}%"
                )

            # 프레임을 JPEG로 인코딩
            ret2, encoded_frame = cv2.imencode(".jpg", frame)
            if not ret2:
                print("[ERROR] 프레임 JPEG 인코딩에 실패했습니다. 다음 루프로 넘어갑니다.")
                continue

            # Queue가 가득 차 있으면 하나 버림
            if frame_queue.full():
                frame_queue.get()

            # 인코딩된 이미지 넣기
            frame_queue.put(encoded_frame)

    camera.release()
    cv2.destroyAllWindows()
