"""
Entrypoint for all server operations.
Needs a state.json file to be present in the same directory as the server.py file or passed in the --state-file argument.
"""

import logging

import utils.parse_args
import utils.parse_state_file


def main():
    args = utils.parse_args.server_parse_args()

    server_state = utils.parse_state_file.parse_state_file(args.state_file)

    logging.info(f"Server started with state: {server_state}")


if __name__ == "__main__":
    main()
