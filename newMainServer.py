##############################################
# newMainServer.py (수정된 버전)
##############################################
from flask import Flask, render_template, Response
from flask_socketio import SocketIO
from camera_manager import CameraManager
import numpy as np
import cv2
import threading
from time import sleep

app = Flask(__name__)
app.config["SECRET_KEY"] = "your_secret_key"
socketio = SocketIO(app, async_mode="eventlet")

# (변경) 프로그램 실행 시, 테스트 모드 여부를 콘솔에서 물어봄
choice = input("서버를 테스트 모드(예: 무작위 이미지)로 실행하시겠습니까? (y/n): ")
TEST_MODE = (choice.lower() == 'y')

# (1) 전역 CameraManager 인스턴스 생성
#     - 만약 테스트 모드이면 카메라 사용하지 않을 수도 있지만,
if not TEST_MODE:
    camera_manager = CameraManager(
        model_path="/home/rpi5/teamproject/keras_model.h5",
        label_path="/home/rpi5/teamproject/labels.txt",
        socketio=socketio  # (중요) socketio 객체를 넘겨줌
    )

@app.route("/")
def index():
    """
    (설명)
    - 기본 페이지 렌더링.
    - 예시: SmartSecuritySystemView.html 등을 사용하면 됩니다.
    """
    return render_template("SmartSecuritySystemView.html")


def gen_frames():
    """
    (수정)
    - TEST_MODE가 True면, 무작위 이미지를 계속 생성하여 스트리밍
    - TEST_MODE가 False면, CameraManager에서 실제 카메라 프레임을 스트리밍
    """
    if TEST_MODE:
        print("[INFO] 테스트 모드: 무작위 이미지를 스트리밍합니다.")
        while True:
            # (변경) 무작위 이미지 생성 (480x640, 컬러 3채널)
            random_image = np.random.randint(0, 256, (480, 640, 3), dtype=np.uint8)
            ret, buffer = cv2.imencode('.jpg', random_image)
            if not ret:
                continue
            frame_data = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_data + b'\r\n')

    else:
        print("[INFO] 실제 카메라 프레임을 스트리밍합니다.")
        while True:
            frame_data = camera_manager.get_frame()
            if frame_data:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_data + b'\r\n')


@app.route("/video_feed")
def video_feed():
    """
    (설명)
    - /video_feed 경로로 접속하는 모든 클라이언트는
      gen_frames()에서 동일한 스트림 데이터를 받음.
    - TEST_MODE 여부에 따라 무작위 이미지 또는 실시간 카메라 영상을 제공.
    """
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@socketio.on("connect")
def on_connect():
    print("[INFO] 클라이언트 접속")

@socketio.on("disconnect")
def on_disconnect():
    print("[INFO] 클라이언트 해제")

@socketio.on("ping_from_web")
def send_pong(data):
    print("[INFO] 클라이언트 ping")
    emit_message("pongs")
    socketio.emit("pong_from_server", {"message": "pong"}, include_self=True)

    # (변경) dict 형태이므로 대괄호[]로 접근
    # 혹은 data.get("message") 사용 가능
    if isinstance(data, dict) and "message" in data:
        print(f"[INFO] {data['message']}")
    else:
        print("[INFO] data에 'message' 키가 없습니다.")

@socketio.on("pong_from_web")
def receive_pong(data):
    print("[INFO] 클라이언트 pong_from_web")

@socketio.on("cam_event")
def receive_pong(data):
    print(f"[INFO] 보낸 메시지: {data['message']}")

def send_event():
    event_message=""
    while True:

        sleep(1)
        emit_message("시발")
        camera_manager.get_event_message()
        if event_message != camera_manager.get_event_message():
            print("event_message: "+event_message)
            event_message = camera_manager.get_event_message()
            emit_message(event_message)
threading.Thread(target=send_event, daemon=True).start()

@socketio.on("get_event_message")
def get_event_message(data):
    print("[INFO] get_event_message")
    emit_message(camera_manager.get_event_message())

def emit_message(message):
    socketio.emit("cam_event", {"message": message}, include_self=True)
    print("emit_message:" + message)



if __name__ == "__main__":
    try:
        # (2) Flask 서버 실행
        #     여러 사용자가 접속해도,
        #     TEST_MODE=False면 CameraManager에서 싱글 스레드 처리
        #     TEST_MODE=True면 무작위 이미지
        socketio.run(app, host="0.0.0.0", port=7000, debug=False)
    finally:
        # (3) 서버 종료 시 카메라 및 스레드 안전 종료
        #     테스트 모드에서도 camera_manager는 초기화했으므로 종료 처리
        camera_manager.stop()
