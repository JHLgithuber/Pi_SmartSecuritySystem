#startup.py
from multiprocessing import Process, Manager
from time import sleep
from webServer import run_flask
from GPIO import run_GPIO
from videoProcessing import run_video_processing
from motorManager import wait_run_motor
from ledManager import wait_run_led
import os
import subprocess

processes = []

shared_dict = {"motor_speed":0, "led_status":"normal"}


def init_processes():
    processes.append({"name": "FlaskServer", "target": run_flask, "process": Process(target=run_flask, args=(shared_dict,event_queue, gpio_queue, live_stream_queue))})
    processes.append({"name": "GPIO", "target": run_GPIO, "process": Process(target=run_GPIO, args=(shared_dict,event_queue, gpio_queue))})
    processes.append({"name": "VideoProcessing", "target": run_video_processing, "process": Process(target=run_video_processing, args=(shared_dict,event_queue, gpio_queue, live_stream_queue))})
    processes.append({"name": "MotorManager", "target": wait_run_motor, "process": Process(target=wait_run_motor, args=(shared_dict,event_queue, gpio_queue))})
    processes.append({"name": "LedManager", "target": wait_run_led, "process": Process(target=wait_run_led, args=(shared_dict, event_queue, gpio_queue))})

    for proc_info in processes:
        proc_info["process"].start()
        print(f"[INFO] Started {proc_info['name']} with PID {proc_info['process'].pid}")

"""
def check_and_restart_process():
    while True:
        sleep(1)
        for proc_info in processes:
            process = proc_info["process"]
            if not process.is_alive():  # 프로세스 종료 확인
                print(f"[WARNING] {proc_info['name']} (PID: {process.pid}) has stopped. Restarting...")
                new_process = Process(target=proc_info["target"], args=(shared_dict,event_queue, gpio_queue))  # 새로운 프로세스 생성
                proc_info["process"] = new_process
                new_process.start()
                print(f"[INFO] Restarted {proc_info['name']} with PID {new_process.pid}")
"""

def terminate_gpio_processes():
    try:
        # `lsof` 명령어로 /dev/gpiomem을 점유 중인 PID 확인
        result = subprocess.check_output(["sudo", "lsof", "-t", "/dev/gpiomem"], text=True)
        pids = result.strip().split("\n")

        if not pids:
            print("[INFO] No GPIO-related processes are running.")
            return

        print(f"[INFO] Found GPIO-related processes: {', '.join(pids)}")
        for pid in pids:
            print(f"[INFO] Terminating process PID: {pid}")
            os.system(f"sudo kill -9 {pid}")
        print("[INFO] All GPIO-related processes have been terminated.")

    except subprocess.CalledProcessError:
        print("[INFO] No GPIO-related processes are running.")


if __name__ == '__main__':
    terminate_gpio_processes()
    manager=Manager()
    shared_dict = manager.dict()  # Manager를 사용하여 공유 딕셔너리 생성
    event_queue = manager.Queue()
    gpio_queue = manager.Queue()
    live_stream_queue = manager.Queue()
    init_processes()
    try:
        while True:
            pass
        #check_and_restart_process()
    except KeyboardInterrupt:
        print("[INFO] Stopping all processes...")
        for proc_info in processes:
            proc_info["process"].terminate()
            print(f"[INFO] Terminated {proc_info['name']} (PID: {proc_info['process'].pid})")
        print("[INFO] All processes stopped.")
