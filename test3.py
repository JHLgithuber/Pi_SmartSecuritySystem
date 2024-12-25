from time import sleep
from gpiozero import DigitalOutputDevice
import cv2

# 모터 핀 설정
IN1 = DigitalOutputDevice(14)  # GPIO14
IN2 = DigitalOutputDevice(15)  # GPIO15
IN3 = DigitalOutputDevice(18)  # GPIO18
IN4 = DigitalOutputDevice(23)  # GPIO23

# LED 핀 설정
red_led = DigitalOutputDevice(3)    # R (GPIO3)
green_led = DigitalOutputDevice(2)  # G (GPIO2)
blue_led = DigitalOutputDevice(4)   # B (GPIO4)

# 스텝 시퀀스 (Half Step)
step_sequence = [
    [1, 0, 0, 0],  # Step 0
    [1, 1, 0, 0],  # Step 1
    [0, 1, 0, 0],  # Step 2
    [0, 1, 1, 0],  # Step 3
    [0, 0, 1, 0],  # Step 4
    [0, 0, 1, 1],  # Step 5
    [0, 0, 0, 1],  # Step 6
    [1, 0, 0, 1],  # Step 7
]

# 현재 스텝
current_step = 0


def set_motor_step(step_gpio):
    """
    모터 핀 상태 설정
    :param step_gpio: 스텝 시퀀스 배열 (4개의 값)
    """
    IN1.value = step_gpio[0]
    IN2.value = step_gpio[1]
    IN3.value = step_gpio[2]
    IN4.value = step_gpio[3]


def rotate_motor(direction, steps, delay=0.005):  # 딜레이를 0.005초로 설정
    """
    모터를 회전시키는 함수
    :param direction: 1 (시계 방향) 또는 -1 (반시계 방향)
    :param steps: 회전할 스텝 수
    :param delay: 각 스텝 간 대기 시간 (초)
    """
    global current_step

    for _ in range(steps):
        if direction == 1:
            # 시계 방향 회전
            current_step = (current_step + 1) % len(step_sequence)
        elif direction == -1:
            # 반시계 방향 회전
            current_step = (current_step - 1) % len(step_sequence)

        # 모터 스텝 상태 설정
        set_motor_step(step_sequence[current_step])
        sleep(delay)  # 각 스텝 간 딜레이 적용


def stop_motor():
    """
    모터를 정지시키는 함수
    """
    set_motor_step([0, 0, 0, 0])  # 모든 핀 OFF


def set_led_color(red, green, blue):
    """
    GBR LED 색상 설정
    :param red: 빨간색 (0 또는 1)
    :param green: 초록색 (0 또는 1)
    :param blue: 파란색 (0 또는 1)
    """
    red_led.value = red
    green_led.value = green
    blue_led.value = blue
    print(f"[INFO] LED 색상 설정 - R: {red}, G: {green}, B: {blue}")


# 얼굴 탐지 및 모터/LED 제어
def control_motor_and_led_based_on_face(frame_center, face_center):
    """
    얼굴 중심과 프레임 중심을 비교하여 모터와 LED를 제어
    :param frame_center: 프레임 중심 (x 좌표)
    :param face_center: 얼굴 중심 (x 좌표)
    """
    # LED 제어: 사람이 인식된 동안 빨간색
    set_led_color(1, 0, 0)

    if abs(face_center - frame_center) < frame_center * 0.1:
        # 얼굴이 중앙에 가까우면 모터 정지
        stop_motor()
        print("[INFO] 얼굴이 중앙에 위치")
    elif face_center < frame_center:
        # 얼굴이 왼쪽에 있으면 모터를 반시계 방향으로 회전
        print("[INFO] 얼굴이 왼쪽에 있음 - 모터 반시계 방향 회전")
        rotate_motor(direction=-1, steps=50, delay=0.005)
    else:
        # 얼굴이 오른쪽에 있으면 모터를 시계 방향으로 회전
        print("[INFO] 얼굴이 오른쪽에 있음 - 모터 시계 방향 회전")
        rotate_motor(direction=1, steps=50, delay=0.005)


if __name__ == "__main__":
    # Haar Cascade 로드
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    # 카메라 초기화
    camera = cv2.VideoCapture(0)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    try:
        while True:
            # 카메라에서 프레임 읽기
            ret, frame = camera.read()
            if not ret:
                print("[ERROR] 카메라에서 프레임을 읽을 수 없습니다.")
                break

            # 그레이스케일로 변환
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # 얼굴 탐지
            faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(50, 50))

            # 프레임 중심 계산
            frame_height, frame_width, _ = frame.shape
            frame_center = frame_width // 2

            if len(faces) > 0:
                # 얼굴이 탐지된 경우
                for (x, y, w, h) in faces:
                    face_center = x + w // 2  # 얼굴 중심 (x 좌표)
                    control_motor_and_led_based_on_face(frame_center, face_center)

                    # 얼굴 영역 표시
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            else:
                # 얼굴이 탐지되지 않으면 LED를 파란색으로 설정
                set_led_color(0, 0, 1)
                print("[INFO] 얼굴이 탐지되지 않음 - LED 파란색 표시")
                stop_motor()  # 얼굴이 없을 경우 모터 정지

            # 프레임 출력
            cv2.imshow("Face Tracking", frame)

            # 'q' 키를 누르면 종료
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        print("\n[INFO] 프로그램 종료 중...")

    finally:
        # 자원 해제
        stop_motor()
        set_led_color(0, 0, 0)  # LED 끄기
        camera.release()
        cv2.destroyAllWindows()
