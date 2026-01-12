import logging
import multiprocessing as mp


def worker(task_queue: mp.JoinableQueue, result_queue: mp.Queue):
    while True:
        job = task_queue.get()
        try:
            logging.info(f"doing job: {job}")
        finally:
            task_queue.task_done()


def start_workers(server_state: dict):
    processCount = mp.cpu_count()

    task_queue = mp.JoinableQueue()
    result_queue = mp.Queue()

    workers = list()

    for _ in range(processCount):
        workers.append(mp.Process(target=lambda: worker(task_queue, result_queue)))

    for worker in workers:
        worker.start()
