__all__ = ["enable_logging"]

import logging
import logging.config
import os
from contextlib import suppress

import yaml


def enable_logging(root_path: str = ".") -> None:
    with suppress(FileNotFoundError):
        path = os.path.join(os.path.realpath(root_path), "logging.yml")
        with open(file=path, mode="r") as stream:
            logging.config.dictConfig(yaml.safe_load(stream))
