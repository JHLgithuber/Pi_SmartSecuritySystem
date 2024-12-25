##############################################
# camera_manager.py (모터 제어 비동기 버전 + LED 제어 연동)
##############################################

import cv2
import numpy as np
import threading
import time

# (변경/추가) gpiozero 라이브러리: 모터/LED 제어
from gpiozero import DigitalOutputDevice

from keras.models import load_model


########################################
# (변경/추가) 1) 별도 스레드로 모터 제어를 수행할 클래스
########################################
class MotorController(threading.Thread):
    def __init__(self, in1, in2, in3, in4, step_sequence):
        super().__init__(daemon=True)
        self.in1 = in1
        self.in2 = in2
        self.in3 = in3
        self.in4 = in4
        self.step_sequence = step_sequence

        self.current_step = 0
        self.direction = 0  # 0=정지, 1=시계, -1=반시계

        # (추가) 스레드 종료 이벤트
        self.stop_event = threading.Event()

        # (추가) 모터 속도 제어(스텝당 sleep 시간)
        self.step_delay = 0.003

    def run(self):
        """
        (설명)
        - 별도 스레드에서 direction값(0/1/-1)에 따라 모터를 돌림
        - 한 번에 너무 많은 스텝을 돌지 않고, 4~5스텝씩 회전 후 다시 확인
        - 이렇게 하면 메인(카메라) 스레드를 블로킹하지 않아 영상이 끊기지 않음
        """
        while not self.stop_event.is_set():
            if self.direction == 0:
                # 모터 정지
                self.set_motor_step([0, 0, 0, 0])
                time.sleep(0.01)
            else:
                # 한 번에 4스텝씩 진행
                steps = 4
                for _ in range(steps):
                    if self.direction == 1:
                        self.current_step = (self.current_step + 1) % len(self.step_sequence)
                    else:  # -1
                        self.current_step = (self.current_step - 1) % len(self.step_sequence)
                    self.set_motor_step(self.step_sequence[self.current_step])
                    time.sleep(self.step_delay)

            time.sleep(0.001)  # CPU 점유율 최소화

    def set_motor_step(self, step_gpio):
        self.in1.value = step_gpio[0]
        self.in2.value = step_gpio[1]
        self.in3.value = step_gpio[2]
        self.in4.value = step_gpio[3]

    def stop_motor(self):
        self.direction = 0
        self.set_motor_step([0, 0, 0, 0])

    def shutdown(self):
        self.stop_event.set()
        self.join()
        self.stop_motor()


########################################
# (변경/추가) 2) CameraManager 클래스: LED 핀 + 모터 + 카메라/딥러닝
########################################
class CameraManager:
    def __init__(self, model_path, label_path, socketio=None):
        # (1) 딥러닝 모델 로드
        self.socketio = socketio
        self.event_message=""
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
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        if not self.camera.isOpened():
            print("[ERROR] 카메라를 열 수 없습니다.")

        # (5) 기타 멤버 변수 초기화
        self.latest_frame = None
        self.running = True
        self.frame_rate = 5  # 초당 처리할 프레임 수
        self.prev_time = time.time()

        # (6) 모터 핀 & 스텝 시퀀스 설정
        self.IN1 = DigitalOutputDevice(14)
        self.IN2 = DigitalOutputDevice(15)
        self.IN3 = DigitalOutputDevice(18)
        self.IN4 = DigitalOutputDevice(23)
        self.step_sequence = [
            [1, 0, 0, 0],
            [1, 1, 0, 0],
            [0, 1, 0, 0],
            [0, 1, 1, 0],
            [0, 0, 1, 0],
            [0, 0, 1, 1],
            [0, 0, 0, 1],
            [1, 0, 0, 1],
        ]

        # (7) LED 핀 설정 (예: R=GPIO3, G=GPIO2, B=GPIO4)
        self.red_led = DigitalOutputDevice(3)
        self.green_led = DigitalOutputDevice(2)
        self.blue_led = DigitalOutputDevice(4)

        # (8) MotorController 스레드 생성 후 시작
        self.motor_controller = MotorController(
            self.IN1, self.IN2, self.IN3, self.IN4,
            self.step_sequence
        )
        self.motor_controller.start()

        # (9) 카메라 스레드 시작
        self.thread = threading.Thread(target=self.update_frames, daemon=True)
        self.thread.start()

    def set_led_color(self, r, g, b):
        """
        (추가) LED 색상 설정 함수
        r, g, b는 0 또는 1
        """
        self.red_led.value = r
        self.green_led.value = g
        self.blue_led.value = b
        # print(f"[INFO] LED 색상: R={r}, G={g}, B={b}")

    def update_frames(self):
        while self.running:
            now = time.time()
            # 프레임레이트 제한
            if now - self.prev_time < 1.0 / self.frame_rate:
                continue
            self.prev_time = now

            ret, frame = self.camera.read()
            if not ret:
                continue

            # === (A) 딥러닝 전처리
            resized_image = cv2.resize(frame, (224, 224), interpolation=cv2.INTER_AREA)
            normalized_image = np.asarray(resized_image, dtype=np.float32).reshape(1, 224, 224, 3)
            normalized_image = (normalized_image / 127.5) - 1.0

            # === (B) 모델 예측
            prediction = self.model.predict(normalized_image)
            index = np.argmax(prediction)
            class_name = self.class_names[index]
            confidence_score = prediction[0][index]

            # === (C) 얼굴 검출
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(
                gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(50, 50)
            )

            frame_height, frame_width, _ = frame.shape
            frame_center = frame_width // 2

            self.socketio.emit("ping_from_server", {
                "message": "ping"
            })



            if len(faces) > 0:
                # 얼굴이 검출됨 -> LED 빨간색
                self.set_led_color(1, 0, 0)




                # 사람이 감지되었다고 가정 (예시)
                self.event_message="사람이 감지되었습니다."

                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                    face_center = x + w // 2

                    offset = face_center - frame_center
                    # 중앙 근처 판정
                    if abs(offset) < frame_center * 0.1:
                        # 모터 정지
                        self.motor_controller.direction = 0
                    elif offset < 0:
                        # 왼쪽이면 반시계
                        self.motor_controller.direction = -1
                    else:
                        # 오른쪽이면 시계
                        self.motor_controller.direction = 1
            else:
                self.event_message = "감지되지 않았습니다."
                # 얼굴이 없음 -> LED 파란색, 모터 정지
                self.set_led_color(0, 0, 1)
                self.motor_controller.direction = 0

            # (E) 디버그 출력
            print(f"[INFO] Class: {class_name}, Confidence: {confidence_score*100:.2f}%")

            # (F) JPEG 인코딩
            ret_jpg, buffer = cv2.imencode('.jpg', frame)
            if ret_jpg:
                self.latest_frame = buffer.tobytes()

    def get_frame(self):
        return self.latest_frame
    def get_event_message(self):
        return self.event_message

    def stop(self):
        # 프로그램 종료 시 안전 종료
        self.running = False
        self.thread.join()
        self.motor_controller.shutdown()  # 모터 스레드 종료

        # LED 끄기
        self.set_led_color(0, 0, 0)

        if self.camera.isOpened():
            self.camera.release()
        cv2.destroyAllWindows()
