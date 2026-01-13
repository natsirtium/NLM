import json
import logging
import os
import typing
from pathlib import Path


def validate_state_data(state_data: dict[str, str]) -> tuple[bool, str]:
    """ """

    REQUIRED_KEYS = []

    POSSIBLE_KEYS = []

    for key, _ in state_data.items():
        if not isinstance(key, str):
            return (False, f"Key {key} must be a string.")

        if key not in POSSIBLE_KEYS:
            return (False, f"Key {key} is not allowed.")

    for key in REQUIRED_KEYS:
        if key not in state_data:
            return (False, f"Key {key} is required.")

    # * Put specific requirements here

    return (True, "")


def parse_state_file(state_file: str) -> dict[str, str]:
    """
    Parse a state file and return a dictionary of key-value pairs.
    """
    path = Path(state_file)

    if not path.is_file():
        logging.error(f"State file {state_file} does not exist.")
        exit(1)

    if not os.access(path, os.R_OK):
        logging.error(f"State file {state_file} is not readable.")
        exit(1)

    logging.info(f"State file {state_file} loaded.")

    with open(state_file, "r") as f:
        try:
            stateLoaded = typing.cast(dict[str, str], json.load(f))
        except json.JSONDecodeError as e:
            logging.error(f"Error loading state file {state_file}: {e}")
            exit(1)

    validation = validate_state_data(stateLoaded)

    if not validation[0]:
        logging.error(f"The state.json file was invalid:\n{validation[1]}")
        exit(1)

    logging.info(f"State file {state_file} validated.")

    return stateLoaded
