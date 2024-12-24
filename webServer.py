# webServer.py
from flask import Flask, render_template, Response
import multiprocessing
import time
from flask_socketio import SocketIO, emit
import base64
import cv2
import numpy as np

app = Flask(__name__)
app.config["SECRET_KEY"] = "your_secret_key"
socketio = SocketIO(app)

stream_queue = None  # live_stream_queue를 저장할 전역 변수


@app.route("/")
def home():
    # 웹 브라우저에서 http://[라즈베리파이IP]:6010/ 에 접근하면 이 함수가 호출
    # templates/SmartSecuritySystemView.html 파일을 보여줌
    return render_template("SmartSecuritySystemView.html")


@app.route("/stream")
def stream():
    global stream_queue
    # MJPEG 스트리밍 응답
    return Response(
        generate_frames(stream_queue),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )


@socketio.on("connect")
def handle_connect():
    print("클라이언트 연결됨")
    emit("notification", {"message": "서버에 연결되었습니다!"})


@socketio.on("message")
def handle_message(data):
    print(f"클라이언트로부터 받은 메시지: {data}")
    emit("response", {"message": f"서버로부터 받은 메시지: {data}"}, broadcast=True)


@socketio.on("disconnect")
def handle_disconnect():
    print("클라이언트 연결 종료됨")


def generate_frames(frame_queue):
    """
    Queue에서 프레임을 가져와 MJPEG로 스트리밍.
    Queue가 비어 있으면 빈(검정) 화면을 전송하여
    무한 로딩이 안 되도록 처리.
    """

    # (A) placeholder (640x480 검정 이미지)
    black_image = np.zeros((480, 640, 3), dtype=np.uint8)
    ret_p, placeholder_encoded = cv2.imencode(".jpg", black_image)
    placeholder_bytes = placeholder_encoded.tobytes() if ret_p else b""

    while True:
        try:
            if not frame_queue.empty():
                encoded_frame = frame_queue.get()
                frame = encoded_frame.tobytes()
            else:
                # Queue가 비어 있으면 placeholder(검정 화면) 전송
                frame = placeholder_bytes

            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
            )
        except Exception as e:
            print(f"[ERROR] generate_frames 예외 발생: {e}")
            time.sleep(0.1)


def run_flask(shared_dict, event_queue, gpio_queue, live_stream_queue):
    """
    Flask + SocketIO 서버를 실행하는 함수.
    """
    global stream_queue
    stream_queue = live_stream_queue
    print("web server process start")

    # Flask-SocketIO의 run() 사용
    socketio.run(app, host="0.0.0.0", port=6020, debug=True)


def worker_task(process_id):
    print(f"프로세스 {process_id} 작업 시작")
    time.sleep(2)
    print(f"프로세스 {process_id} 작업 완료")


if __name__ == "__main__":
    # 단독 실행 테스트용
    mgr = multiprocessing.Manager()
    test_queue = mgr.Queue()
    run_flask(None, None, None, test_queue)
