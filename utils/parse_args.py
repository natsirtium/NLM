import argparse
import logging
from typing import cast


class ServerArgs:
    def __init__(self, state_file: str, verbose: bool) -> None:
        self.state_file: str = state_file
        self.verbose: bool = verbose


def server_parse_args():
    """
    Parses command line arguments for the server.

    Returns:
        ServerArgs: An instance of ServerArgs containing the parsed arguments.
    """
    parser = argparse.ArgumentParser(
        prog="nlm-server",
        description="Entrypoint for all server operations.",
        epilog="Needs a state.json file to be present in the same directory as the server.py file or passed in the --state-file argument.",
    )

    _ = parser.add_argument("--state-file", type=str, help="Path to the state file.")
    _ = parser.add_argument(
        "--verbose", action="store_true", help="Enable verbose logging."
    )
    args = parser.parse_args()

    state_file = cast(str | None, args.state_file)
    verbose = cast(bool, args.verbose)

    if state_file is None:
        state_file = "state.json"

    if verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    server_args = ServerArgs(state_file, verbose)

    return server_args
