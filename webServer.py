from flask import Flask
import multiprocessing
import time

# Flask 애플리케이션 정의
app = Flask(__name__)

@app.route("/")
def home():
    return "Hello, Flask is running in a process!"

def run_flask():
    """
    Flask 애플리케이션을 실행하는 함수.
    """
    app.run(host="127.0.0.1", port=5000, debug=False)

def worker_task(process_id):
    """
    다른 프로세스에서 실행될 일반 작업.
    """
    print(f"프로세스 {process_id} 작업 시작")
    time.sleep(2)
    print(f"프로세스 {process_id} 작업 완료")

if __name__ == "__main__":
    # Flask를 실행하는 프로세스
    flask_process = multiprocessing.Process(target=run_flask)

    # 기타 작업을 처리하는 워커 프로세스
    worker_process = multiprocessing.Process(target=worker_task, args=(1,))

    # 프로세스 시작
    flask_process.start()
    worker_process.start()

    # 모든 프로세스가 종료될 때까지 대기
    worker_process.join()
    flask_process.terminate()  # Flask 프로세스 종료

    print("모든 작업 완료!")
