import logging
import multiprocessing as mp
import typing
from enum import Enum, auto
from pathlib import Path
from uuid import UUID

import server_io
from server_io import Client


class Job_Types(Enum):
    RECEIVE_AND_STAGE = auto()
    SAVE_STAGED_FILE = auto()


class Job:
    def __init__(
        self,
        type: Job_Types,
        staged_file_path: str | None = None,
        client: Client | None = None,
        file_uuid: UUID | None = None,
    ):
        match type:
            case Job_Types.RECEIVE_AND_STAGE:
                self.client = client
                self.file_uuid = file_uuid

            case Job_Types.SAVE_STAGED_FILE:
                if not staged_file_path:
                    logging.error(
                        "Attempted to start a SAVE_STAGED_FILE job without define a staged_file_path."
                    )
                    return False

                staged_file_path = typing.cast(str, staged_file_path)

                if not Path(staged_file_path).is_file():
                    logging.error(f'Could not find staged file "{staged_file_path}"')

                self.job_type = type
                self.staged_file_path = staged_file_path


class Worker_Manager:
    def __init__(self, task_queue: mp.JoinableQueue, workers: list[mp.Process]):
        self.task_queue = task_queue


def do_job(job: Job):
    match job.job_type:
        case Job_Types.RECEIVE_AND_STAGE:
            server_io.receive_and_stage(job)
        case Job_Types.SAVE_STAGED_FILE:
            server_io.save_staged_file(job)


def worker(task_queue: mp.JoinableQueue):
    while True:
        job = task_queue.get()
        try:
            logging.info(f"doing job: {job}")
        finally:
            task_queue.task_done()


def start_workers(server_state: dict):
    processCount = mp.cpu_count()

    task_queue = mp.JoinableQueue()

    workers = list()

    for _ in range(processCount):
        workers.append(mp.Process(target=lambda: worker(task_queue)))

    for worker in workers:
        worker.start()

    worker_manager = Worker_Manager(task_queue, workers)

    return worker_manager
