import logging
import os
from fire import Fire
import yaml

from firestation_clustering.commands_handler import CommandsHandler


def chunker(seq, size):
    return (seq[pos : pos + size] for pos in range(0, len(seq), size))


def load_config():
    config = {}
    with open("config.yaml") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    return config


def configure_logging():
    log_format = "%(asctime)s [%(levelname)s] %(module)s.%(funcName)s(): %(message)s"
    logging.basicConfig(level=logging.INFO, format=log_format)


def main():
    config = load_config()
    configure_logging()
    logging.info("Hello")

    if not os.path.exists("out"):
        os.makedirs("out")

    commands = CommandsHandler(config)
    Fire(commands)
