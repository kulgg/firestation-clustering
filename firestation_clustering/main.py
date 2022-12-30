import logging
import yaml

from firestation_clustering.maps import Maps


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
    maps = Maps(config["gmaps"])
    maps.set_city("Berlin")

    for _ in range(10):
        logging.info(maps.get_random_point())
