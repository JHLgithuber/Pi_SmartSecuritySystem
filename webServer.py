#webServer.py
from flask import Flask, render_template, Response
import multiprocessing
import time
from flask_socketio import SocketIO, emit

# Flask 애플리케이션 정의
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # 비밀키 설정
socketio = SocketIO(app)  # Flask-SocketIO 초기화

@app.route("/")
def home():
    return render_template("SmartSecuritySystemView.html")

@app.route('/stream')
def stream():
    global stream_queue
    return Response(generate_frames(stream_queue), mimetype='multipart/x-mixed-replace; boundary=frame')


@socketio.on('connect')  # 클라이언트 연결 시
def handle_connect():
    print('클라이언트 연결됨')
    emit('notification', {'message': '서버에 연결되었습니다!'})  # 클라이언트로 알림 전송

@socketio.on('message')  # 'message' 이벤트 처리
def handle_message(data):
    print(f'클라이언트로부터 받은 메시지: {data}')
    emit('response', {'message': f"서버로부터 받은 메시지: {data}"}, broadcast=True)  # 응답 및 브로드캐스트

@socketio.on('disconnect')  # 클라이언트 연결 종료 시
def handle_disconnect():
    print('클라이언트 연결 종료됨')


def generate_frames(frame_queue):
    while True:
        if not frame_queue.empty():
            img = frame_queue.get()
            print(img)# 큐에서 최신 프레임 가져오기
            frame = img.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        else:
            time.sleep(0.03)

def run_flask(shared_dict,event_queue, gpio_queue, live_stream_queue):
    global stream_queue
    stream_queue = live_stream_queue
    print("web server process start")
    """
    Flask 애플리케이션을 실행하는 함수.
    """
    app.run(host="0.0.0.0", port=6010, debug=True)

def worker_task(process_id):
    """
    다른 프로세스에서 실행될 일반 작업.
    """
    print(f"프로세스 {process_id} 작업 시작")
    time.sleep(2)
    print(f"프로세스 {process_id} 작업 완료")


if __name__ == "__main__":
    run_flask(None, None)
