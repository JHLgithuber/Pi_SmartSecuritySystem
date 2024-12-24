#motorManager.py

from time import sleep




MAX_SPEED_DELAY = 0.001
MIN_SPEED_DELAY = 0.05



# 스텝 시퀀스
step_sequence = [
    [1, 0, 0, 0],  # Step 0
    [1, 1, 0, 0],  # Step 1
    [0, 1, 0, 0],  # Step 2
    [0, 1, 1, 0],  # Step 3
    [0, 0, 1, 0],  # Step 4
    [0, 0, 1, 1],  # Step 5
    [0, 0, 0, 1],  # Step 6
    [1, 0, 0, 1],  # Step 7
]

# 현재 스텝 인덱스
current_step = 0
gpio_queue=None





def set_step(w_list):
    """스텝 설정"""
    gpio_queue.put({"step_gpio": w_list})



def set_next_step():
    """다음 스텝으로 이동"""
    global current_step
    current_step = (current_step + 1) % len(step_sequence)
    set_step(step_sequence[current_step])


def set_prev_step():
    """이전 스텝으로 이동"""
    global current_step
    current_step = (current_step - 1) % len(step_sequence)
    set_step(step_sequence[current_step])


def run_motor(speed_percent):
    """
    스텝모터를 속도 백분율로 제어
    - speed_percent > 0: 시계 방향
    - speed_percent < 0: 반시계 방향
    - speed_percent == 0: 정지
    """
    delay = MIN_SPEED_DELAY - ((MIN_SPEED_DELAY - MAX_SPEED_DELAY) * (abs(speed_percent) / 100))

    if speed_percent == 0:
        set_step([0,0,0,0])  # 모든 핀 OFF
    elif speed_percent > 0:
        set_next_step()
        sleep(delay)
    elif speed_percent < 0:
        set_prev_step()
        sleep(delay)

def motor_test():
    for i in range(-1000, 1000):  # -100% ~ 100% 속도로 회전
        run_motor(100)
    for i in range(1000, -1000, -1):  # 100% ~ -100% 반대로 회전
        run_motor(-100)


def wait_run_motor(shared_dict,event_queue,gpio_queue_input):
    global gpio_queue
    gpio_queue = gpio_queue_input
    print("motor process start")
    while True:
        motor_test()
        print("motor process run")
