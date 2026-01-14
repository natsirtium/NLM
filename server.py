"""
Entrypoint for all server operations.
Needs a state.json file to be present in the same directory as the server.py file or passed in the --state-file argument.
"""

import logging
import multiprocessing as mp

import server_source.server_io as server_io
import server_source.worker_manager as wm
import utils.parse_args
import utils.parse_state_file


def main():
    args = utils.parse_args.server_parse_args()

    server_state = utils.parse_state_file.parse_state_file(args.state_file)

    worker_manager = wm.start_workers(
        server_state, 1
    )  # Reserve 1 for client manager thread

    server = server_io.init_server()

    server_thread = mp.Process(
        target=server_io.server_thread,
        args=(
            server.socket,
            worker_manager.task_queue,
        ),
    )

    server_thread.start()

    logging.info(f"Server started on port {server_io.PORT}.")


if __name__ == "__main__":
    main()
