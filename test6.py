import cv2
import numpy as np
import threading
import time

from gpiozero import DigitalOutputDevice
from keras.models import load_model
import pygame

########################################
# 모터 제어 스레드 클래스
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
        self.direction = 0
        self.stop_event = threading.Event()
        self.step_delay = 0.003

    def run(self):
        while not self.stop_event.is_set():
            if self.direction == 0:
                self.set_motor_step([0, 0, 0, 0])
                time.sleep(0.01)
            else:
                steps = 4
                for _ in range(steps):
                    if self.direction == 1:
                        self.current_step = (self.current_step + 1) % len(self.step_sequence)
                    else:
                        self.current_step = (self.current_step - 1) % len(self.step_sequence)
                    self.set_motor_step(self.step_sequence[self.current_step])
                    time.sleep(self.step_delay)

            time.sleep(0.001)

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
# CameraManager 클래스
########################################
class CameraManager:
    def __init__(self, model_path, label_path, socketio=None):
        # 딥러닝 모델 로드
        self.socketio = socketio
        self.event_message = ""
        self.model = load_model(model_path, compile=False)

        # 레이블 로드
        with open(label_path, "r") as f:
            self.class_names = [line.strip() for line in f.readlines()]

        # Haar Cascade(얼굴 검출기) 로드
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )

        # 카메라 초기화
        self.camera = cv2.VideoCapture(0)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        if not self.camera.isOpened():
            print("[ERROR] 카메라를 열 수 없습니다.")

        self.latest_frame = None
        self.running = True
        self.frame_rate = 5
        self.prev_time = time.time()

        # 모터 핀 & 스텝 시퀀스 설정
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

        # LED 핀 설정
        self.red_led = DigitalOutputDevice(3)
        self.green_led = DigitalOutputDevice(2)
        self.blue_led = DigitalOutputDevice(4)

        self.motor_controller = MotorController(
            self.IN1, self.IN2, self.IN3, self.IN4,
            self.step_sequence
        )
        self.motor_controller.start()

        self.thread = threading.Thread(target=self.update_frames, daemon=True)
        self.thread.start()

        # 사운드 관련 초기화
        pygame.mixer.init()
        self.sound_file = "/path/to/your/sound.mp3"  # 경로를 적절히 수정하세요
        self.is_playing_sound = False

    def set_led_color(self, r, g, b):
        self.red_led.value = r
        self.green_led.value = g
        self.blue_led.value = b

        if r == 1 and not self.is_playing_sound:
            self.play_sound()
        elif b == 1 and self.is_playing_sound:
            self.stop_sound()

    def play_sound(self):
        pygame.mixer.music.load(self.sound_file)
        pygame.mixer.music.play(-1)
        self.is_playing_sound = True

    def stop_sound(self):
        pygame.mixer.music.stop()
        self.is_playing_sound = False

    def update_frames(self):
        while self.running:
            now = time.time()
            if now - self.prev_time < 1.0 / self.frame_rate:
                continue
            self.prev_time = now

            ret, frame = self.camera.read()
            if not ret:
                continue

            resized_image = cv2.resize(frame, (224, 224), interpolation=cv2.INTER_AREA)
            normalized_image = np.asarray(resized_image, dtype=np.float32).reshape(1, 224, 224, 3)
            normalized_image = (normalized_image / 127.5) - 1.0

            prediction = self.model.predict(normalized_image)
            index = np.argmax(prediction)
            class_name = self.class_names[index]

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
                self.set_led_color(1, 0, 0)
                self.event_message = "사람이 감지되었습니다."
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                    face_center = x + w // 2
                    offset = face_center - frame_center

                    # 네모 박스 위에 라벨 추가
                    cv2.putText(
                        frame, class_name, (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2
                    )

                    if abs(offset) < frame_center * 0.1:
                        self.motor_controller.direction = 0
                    elif offset < 0:
                        self.motor_controller.direction = -1
                    else:
                        self.motor_controller.direction = 1
            else:
                self.set_led_color(0, 0, 1)
                self.event_message = "감지되지 않았습니다."
                self.motor_controller.direction = 0

            ret_jpg, buffer = cv2.imencode('.jpg', frame)
            if ret_jpg:
                self.latest_frame = buffer.tobytes()

    def get_frame(self):
        return self.latest_frame

    def get_event_message(self):
        return self.event_message

    def stop(self):
        self.running = False
        self.thread.join()
        self.motor_controller.shutdown()

        self.set_led_color(0, 0, 0)
        self.stop_sound()

        if self.camera.isOpened():
            self.camera.release()
        cv2.destroyAllWindows()
