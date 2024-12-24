#webServer.py
from flask import Flask, render_template
import multiprocessing
import time

# Flask 애플리케이션 정의
app = Flask(__name__)

@app.route("/")
def home():
    return render_template("SmartSecuritySystemView.html")

def run_flask(shared_dict,event_queue, gpio_queue):
    print("web server process start")
    """
    Flask 애플리케이션을 실행하는 함수.
    """
    app.run(host="0.0.0.0", port=5000, debug=True)

def worker_task(process_id):
    """
    다른 프로세스에서 실행될 일반 작업.
    """
    print(f"프로세스 {process_id} 작업 시작")
    time.sleep(2)
    print(f"프로세스 {process_id} 작업 완료")


if __name__ == "__main__":
    run_flask(None, None)
