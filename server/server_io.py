import logging
import socket

from worker_manager import Job

HOST = "0.0.0.0"
PORT = 9000


class Client:
    pass


def init_server() -> socket.socket:
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    logging.info(f"Server started with host {HOST} on port {PORT}.")

    return server


def receive_and_stage(job: Job):
    pass


def save_staged_file(job: Job):
    pass
