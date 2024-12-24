#ledManager.py

from time import sleep
gpio_queue=None



def set_color(red, green, blue):
    global gpio_queue
    """GBR LED 색상 설정 (0~1)"""
    gpio_queue.put({"rgb_gpio":[1-red,1-green,1-blue]})


def round_color():
    set_color(1, 0, 0)
    sleep(1)
    set_color(0, 1, 0)
    sleep(1)
    set_color(0, 0, 1)
    sleep(1)
    set_color(1, 1, 0)
    sleep(1)
    set_color(0, 1, 1)
    sleep(1)
    set_color(1, 0, 1)
    sleep(1)
    set_color(1, 1, 1)
    sleep(1)

def wait_run_led(shared_dict, event_queue, gpio_queue_arg):
    global gpio_queue
    gpio_queue = gpio_queue_arg

    print("LED process start")
    while True:
        set_color(0.5,0.5,0.5)
        sleep(5)
        round_color()
        print("LED process run")
