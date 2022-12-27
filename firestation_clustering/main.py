import logging
import yaml


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
    logging.info("hello")
    logging.info(config)
