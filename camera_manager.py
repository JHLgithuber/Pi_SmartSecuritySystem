##############################################
# camera_manager.py
##############################################
import cv2
import numpy as np
import threading
import time
from keras.models import load_model

class CameraManager:
    def __init__(self, model_path, label_path):
        """
        (설명)
        - 카메라를 한 번만 열고, 별도의 스레드에서 무한 루프를 돌면서
          1) 프레임 읽기
          2) 딥러닝 추론(keras_model.h5)
          3) 얼굴 검출(Haar Cascade)
          4) 최종 결과를 JPEG로 인코딩 → latest_frame 보관

        - 여러 사용자가 접근해도 카메라&모델 추론이 단 한 번만 일어납니다.
        """
        # (1) 딥러닝 모델 로드
        self.model = load_model(model_path, compile=False)
        # (2) 레이블 로드
        with open(label_path, "r") as f:
            self.class_names = [line.strip() for line in f.readlines()]

        # (3) Haar Cascade(얼굴 검출기) 로드
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )

        # (4) 카메라 초기화
        self.camera = cv2.VideoCapture(0)
        # 해상도 설정 (성능 문제 있으면 조절)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        if not self.camera.isOpened():
            print("[ERROR] 카메라를 열 수 없습니다.")
            # 실제 사용 환경에서 예외 처리나 종료 로직 추가 가능.

        # (5) 멤버 변수 초기화
        self.latest_frame = None    # 딥러닝+얼굴 검출 후 JPEG 바이트
        self.running = True         # 스레드 루프를 제어하는 플래그
        self.frame_rate = 3         # 초당 처리할 프레임 수(줄이면 CPU 부담 감소)
        self.prev_time = time.time()

        # (6) 스레드 시작
        self.thread = threading.Thread(target=self.update_frames, daemon=True)
        self.thread.start()

    def update_frames(self):
        """
        (설명)
        - 별도 스레드에서 카메라를 지속적으로 읽어서,
          딥러닝 추론 및 얼굴 검출 후, latest_frame에 보관.
        """
        while self.running:
            now = time.time()
            # 프레임레이트 제한
            if now - self.prev_time < 1.0 / self.frame_rate:
                continue
            self.prev_time = now

            ret, frame = self.camera.read()
            if not ret:
                continue

            # === (A) 딥러닝 전처리 ===
            resized_image = cv2.resize(frame, (224, 224), interpolation=cv2.INTER_AREA)
            normalized_image = np.asarray(resized_image, dtype=np.float32).reshape(1, 224, 224, 3)
            normalized_image = (normalized_image / 127.5) - 1.0

            # === (B) 모델 예측 ===
            prediction = self.model.predict(normalized_image)
            index = np.argmax(prediction)
            class_name = self.class_names[index]
            confidence_score = prediction[0][index]

            # === (C) 얼굴 검출 ===
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(
                gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(50, 50)
            )

            # (D) 검출된 얼굴에 사각형 등 시각화
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

            # (E) 콘솔 출력(필요 시 주기적으로만 가능)
            print(f"[INFO] Class: {class_name}, Confidence: {confidence_score*100:.2f}%")

            # (F) JPEG 인코딩
            ret_jpg, buffer = cv2.imencode('.jpg', frame)
            if ret_jpg:
                self.latest_frame = buffer.tobytes()

    def get_frame(self):
        """
        (설명)
        - Flask 쪽에서 호출하여, 스레드에서 저장해둔 최신 JPEG 바이트를 반환.
        """
        return self.latest_frame

    def stop(self):
        """
        (설명)
        - 서버 종료 시점 등에 카메라와 스레드를 안전하게 종료하기 위해 호출.
        """
        self.running = False
        self.thread.join()
        if self.camera.isOpened():
            self.camera.release()
        cv2.destroyAllWindows()
