import random
from time import sleep

from gpiozero import DigitalOutputDevice
from gpiozero import PWMLED

# 핀 설정
IN1 = DigitalOutputDevice(14)
IN2 = DigitalOutputDevice(15)
IN3 = DigitalOutputDevice(18)
IN4 = DigitalOutputDevice(23)

# GBR LED 설정
green_led = PWMLED(2)  # G (GPIO2)
blue_led = PWMLED(3)  # B (GPIO3)
red_led = PWMLED(4)  # R (GPIO4)


def set_motorDriver(step_gpio):
    IN1.value = step_gpio[0]
    IN2.value = step_gpio[1]
    IN3.value = step_gpio[2]
    IN4.value = step_gpio[3]

def set_led(rgb_gpio):
    red_led.value = rgb_gpio[0]
    green_led.value = rgb_gpio[1]
    blue_led.value = rgb_gpio[2]



def run_GPIO(shared_dict, event_queue, gpio_queue):
    while True:
        while not gpio_queue.empty():
            gpio_command = gpio_queue.get()
            print(gpio_command)
            rgb_gpio = gpio_command.get("rgb_gpio")
            step_gpio = gpio_command.get("step_gpio")

            if not rgb_gpio is None:
                # print(red_gpio)
                set_led(rgb_gpio)
            if not step_gpio is None:
                # print(step_gpio)
                set_motorDriver(step_gpio)

            sleep(0.001)
            # print("GPIO process run")



if __name__ == "__main__":
    while True:
        set_motorDriver([1, 1, 1, 1])
        set_led([random.random(),random.random(),random.random()])
