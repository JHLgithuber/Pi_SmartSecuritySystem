#vidoeProcessing.py
from time import sleep


def run_video_processing(shared_dict,event_queue, gpio_queue):
    print("Video Process start")
    while True:
        print("Video Process run")

        sleep(10)
