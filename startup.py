# startup.py
from multiprocessing import Process, Manager
from time import sleep
import os
import subprocess

from webServer import run_flask
from GPIO import run_GPIO  # 질문 내용상 GPIO.py가 있다고 가정
from videoProcessing import run_video_processing
from motorManager import wait_run_motor  # 질문 내용상 motorManager.py가 있다고 가정
from ledManager import wait_run_led      # 질문 내용상 ledManager.py가 있다고 가정


processes = []

def terminate_gpio_processes():
    """
    /dev/gpiomem을 사용하는 모든 프로세스를 강제 종료하기 위한 유틸 함수.
    """
    try:
        result = subprocess.check_output(["sudo", "lsof", "-t", "/dev/gpiomem"], text=True)
        pids = result.strip().split("\n")

        if not pids or pids == ['']:
            print("[INFO] No GPIO-related processes are running.")
            return

        print(f"[INFO] Found GPIO-related processes: {', '.join(pids)}")
        for pid in pids:
            if pid.strip():
                print(f"[INFO] Terminating process PID: {pid}")
                os.system(f"sudo kill -9 {pid}")
        print("[INFO] All GPIO-related processes have been terminated.")

    except subprocess.CalledProcessError:
        print("[INFO] No GPIO-related processes are running.")


def init_processes(shared_dict, event_queue, gpio_queue, live_stream_queue):
    """
    여러 프로세스를 초기화하고 실행.
    """

    # Flask 서버 프로세스
    processes.append({
        "name": "FlaskServer",
        "target": run_flask,
        "process": Process(
            target=run_flask,
            args=(shared_dict, event_queue, gpio_queue, live_stream_queue)
        )
    })

    # GPIO 프로세스
    processes.append({
        "name": "GPIO",
        "target": run_GPIO,
        "process": Process(
            target=run_GPIO,
            args=(shared_dict, event_queue, gpio_queue)
        )
    })

    # 영상처리 프로세스
    processes.append({
        "name": "VideoProcessing",
        "target": run_video_processing,
        "process": Process(
            target=run_video_processing,
            args=(shared_dict, event_queue, gpio_queue, live_stream_queue)
        )
    })

    # 모터 프로세스
    processes.append({
        "name": "MotorManager",
        "target": wait_run_motor,
        "process": Process(
            target=wait_run_motor,
            args=(shared_dict, event_queue, gpio_queue)
        )
    })

    # LED 프로세스
    processes.append({
        "name": "LedManager",
        "target": wait_run_led,
        "process": Process(
            target=wait_run_led,
            args=(shared_dict, event_queue, gpio_queue)
        )
    })

    # 프로세스 실행
    for proc_info in processes:
        proc_info["process"].start()
        print(f"[INFO] Started {proc_info['name']} with PID {proc_info['process'].pid}")


if __name__ == '__main__':
    # 1) 기존에 GPIO를 점유 중인 프로세스가 있으면 종료
    terminate_gpio_processes()

    # 2) Manager로 공유 자원 생성
    manager = Manager()
    shared_dict = manager.dict({
        "motor_speed": 0,
        "led_status": "normal"
    })
    event_queue = manager.Queue()
    gpio_queue = manager.Queue()
    live_stream_queue = manager.Queue()

    # 3) 프로세스 초기화 & 실행
    init_processes(shared_dict, event_queue, gpio_queue, live_stream_queue)

    try:
        # 메인 프로세스는 종료될 때까지 대기
        while True:
            sleep(1)  # CPU 점유율 방지
    except KeyboardInterrupt:
        print("[INFO] Stopping all processes...")
        for proc_info in processes:
            proc_info["process"].terminate()
            print(f"[INFO] Terminated {proc_info['name']} (PID: {proc_info['process'].pid})")
        print("[INFO] All processes stopped.")
