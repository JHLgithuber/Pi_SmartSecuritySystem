from flask import Flask, render_template
from flask_socketio import SocketIO
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

# Flask-SocketIO 초기화
socketio = SocketIO(app)

# 주기적으로 메시지를 보내는 함수
def send_messages():
    while True:
        time.sleep(5)  # 5초 간격
        socketio.emit('server_message', {'data': '정기 메시지입니다!'})

# Flask 라우트
@app.route('/')
def index():
    return render_template('socketio_test_html.html')

# 백그라운드 스레드 실행
@socketio.on('connect')
def handle_connect():
    print('클라이언트 연결됨')
    # 클라이언트 연결 시 백그라운드 태스크 실행
    socketio.start_background_task(send_messages)

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=7000, debug=False)
