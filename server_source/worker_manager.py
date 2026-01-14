import logging
import multiprocessing as mp
import typing
from enum import Enum, auto
from pathlib import Path
from uuid import UUID

from . import server_io


class Job_Types(Enum):
    RECEIVE_AND_STAGE = auto()
    SAVE_STAGED_FILE = auto()
    GET_LATEST = auto()
    CHECKOUT = auto()
    CHECKIN = auto()


class Job:
    def __init__(
        self,
        type: Job_Types,
        staged_file_path: str | None = None,
        client: server_io.Client | None = None,
        file_uuids: list[UUID] | None = None,
    ):
        match type:
            case Job_Types.RECEIVE_AND_STAGE:
                if not self.client:
                    logging.error(
                        "Attempted to start a RECEIVE_AND_STAGE job without a client."
                    )
                    return False

                if not self.file_uuids:
                    logging.error(
                        "Attempted to start a RECEIVE_AND_STAGE job without file_uuids."
                    )
                    return False

                self.client = client
                self.file_uuids = file_uuids

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

            case _:
                logging.warning("Unknown job type")


class Worker_Manager:
    def __init__(self, task_queue: mp.JoinableQueue, workers: list[mp.Process]):
        self.task_queue = task_queue
        self.client_manager_threads = list()


def do_job(job: Job) -> None:
    match job.job_type:
        case Job_Types.RECEIVE_AND_STAGE:
            server_io.receive_and_stage(job)
        case Job_Types.SAVE_STAGED_FILE:
            server_io.save_staged_file(job)


def worker(task_queue: mp.JoinableQueue) -> None:
    while True:
        job = task_queue.get()
        try:
            logging.info(f"doing job: {job}")
            do_job(job)
        finally:
            task_queue.task_done()


def start_workers(server_state: dict, reserved_threads: int = 0) -> Worker_Manager:
    """
    Starts all of the workers, returns a Worker_Manager object.

    server_state | Dictionary, see parse_state_file.py for format
    left_threads | Numb of threads to attempt to leave for other operations. respected as long as a minimum of 1 is kept for jobs.

    """
    try:
        ctx = mp.get_context("fork")
    except ValueError:
        ctx = mp.get_context()

    core_count = mp.cpu_count()

    if reserved_threads >= core_count:
        usable_cores = 1
        logging.warning(
            "Attempted to reserve more threads than available from workers."
        )
    else:
        usable_cores = core_count - reserved_threads

    task_queue = ctx.JoinableQueue()

    workers = list()

    for _ in range(usable_cores):
        workers.append(ctx.Process(target=worker, args=(task_queue,)))

    for proc in workers:
        proc.start()

    worker_manager = Worker_Manager(task_queue, workers)

    return worker_manager
