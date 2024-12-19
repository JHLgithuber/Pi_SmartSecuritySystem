import multiprocessing
import time

def worker(process_id):
    """
    각 프로세스에서 실행될 작업 함수.
    :param process_id: 프로세스 ID를 전달받아 출력.
    """
    print(f"프로세스 {process_id} 시작!")
    # 작업 시뮬레이션 (3초 대기)
    time.sleep(3)
    print(f"프로세스 {process_id} 완료!")

if __name__ == "__main__":
    # 총 실행할 프로세스 수
    num_processes = 5

    # 프로세스를 담을 리스트
    processes = []

    # 여러 개의 프로세스 생성 및 시작
    for i in range(num_processes):
        process = multiprocessing.Process(target=worker, args=(i,))
        processes.append(process)
        process.start()

    # 모든 프로세스가 종료될 때까지 대기
    for process in processes:
        process.join()

    print("모든 프로세스 완료!")
