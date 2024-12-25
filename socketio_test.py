from flask import Flask, render_template
from flask_socketio import SocketIO
import time
import threading

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

# Flask-SocketIO 초기화
socketio = SocketIO(app)

# 주기적으로 메시지를 보내는 함수
def send_messages():
    while True:
        time.sleep(5)  # 5초 간격
        socketio.emit('server_message', {'data': '정기 메시지입니다!'}, broadcast=True)

# Flask 라우트
@app.route('/')
def index():
    return render_template('socketio_test.html')

# 백그라운드로 메시지 전송 스레드 실행
@app.before_first_request
def start_background_thread():
    threading.Thread(target=send_messages, daemon=True).start()

if __name__ == '__main__':
    socketio.run(app, debug=True)
