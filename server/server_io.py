"""


A note about conventions: In all IO operations, untrusted values should **always** start with `u_`.
Never directly use a untrusted value, always read what you need out of it, cast it, verify it, *then* use it.
"""

import logging
import multiprocessing as mp
import socket
import threading
import uuid

from worker_manager import Job, Job_Types

HOST = "0.0.0.0"
PORT = 9000


class Client:
    def __init__(self, conn, addr):
        self.connection_open = True
        self.conn = conn
        self.addr = addr


class Communication:
    def __init__(self, u_message: str, client: Client):
        self.u_message = u_message
        self.client = client

    def parse(self, task_queue: mp.JoinableQueue) -> bool:
        u_subrequests = self.u_message.split("|")

        u_message_type = u_subrequests[0]

        match u_message_type:
            case "CLOSE_CONNECTION":
                self.client.connection_open = False
            case "COMMIT_CHANGES":
                if not len(u_subrequests) == 2:
                    logging.warning(
                        f"Invalid number of subrequests for COMMIT_CHANGES: {len(u_subrequests)}"
                    )
                    return False

                u_uuids = u_subrequests[1].split("_")

                if u_uuids == "":
                    logging.warning("No UUIDs provided for COMMIT_CHANGES")
                    return False

                uuids = list()

                for u_uuid in u_uuids:
                    try:
                        u_UUID = uuid.UUID(u_uuid)
                        if not u_UUID.version == 1:
                            logging.warning(f"Invalid UUID version: {u_UUID.version}")
                            return False

                        uuids.append(u_UUID)
                    except ValueError:
                        logging.warning(f"Invalid UUID: {u_uuid}")
                        return False

                job = Job(
                    Job_Types.RECEIVE_AND_STAGE, client=self.client, file_uuids=uuids
                )
                task_queue.put(job)

            case _:
                logging.warning("Unrecognized request type received.")

        return True


def init_server() -> socket.socket:
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    logging.info(f"Server started with host {HOST} on port {PORT}.")

    return server


def client_manager_thread(conn, addr, task_queue: mp.JoinableQueue):
    logging.info(f"Connected to {addr}.")

    client = Client(conn, addr)

    try:
        while True:
            u_data = conn.recv(4096)  # Any larger files should be handled by a worker
            if not u_data:
                break

            com = Communication(u_data.decode(), client)

            com.parse(task_queue)

    finally:
        conn.close()
        logging.info(f"Disconected from {addr}")


def server_thread(
    server: socket.socket,
    task_queue: mp.JoinableQueue,
    client_manager_threads: list[threading.Thread],
):
    while True:
        conn, addr = server.accept()

        thread = threading.Thread(
            target=lambda: client_manager_thread(conn, addr, task_queue), daemon=True
        )
        thread.start()
        client_manager_threads.append(thread)


def receive_and_stage(job: Job):
    pass


def save_staged_file(job: Job):
    pass
