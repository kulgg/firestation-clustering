import logging
import os
from fire import Fire
import yaml
from sklearn.cluster import KMeans

from firestation_clustering.maps import Maps


def load_config():
    config = {}
    with open("config.yaml") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    return config


def configure_logging():
    log_format = "%(asctime)s [%(levelname)s] %(module)s.%(funcName)s(): %(message)s"
    logging.basicConfig(level=logging.INFO, format=log_format)


class CommandsHandler:
    def __init__(self, config):
        self.config = config

    def kmeans_euclid(self, city, num_stations, num_fires=300, iterations=10):
        maps = Maps(self.config["gmaps"])
        maps.set_city(city)

        fire_stations = []
        for i in range(num_stations):
            lat, lng = maps.get_random_point()
            fire_stations.append((lat, lng))

        for i in range(iterations):
            fires = []
            for _ in range(num_fires):
                lat, lng = maps.get_random_point()
                fires.append((lat, lng))

            map_img = maps.get_city_map(fires, fire_stations)

            city_dir_path = f"out/{city}"
            if not os.path.exists(city_dir_path):
                os.makedirs(city_dir_path)

            with open(f"out/{city}/{i}.png", "wb") as f:
                for chunk in map_img:
                    if chunk:
                        f.write(chunk)

            kmeans = KMeans(
                n_clusters=num_stations, init=fire_stations, n_init=1, max_iter=1
            ).fit(fires)
            fire_stations = kmeans.cluster_centers_


def main():
    config = load_config()
    configure_logging()
    logging.info("Hello")

    if not os.path.exists("out"):
        os.makedirs("out")

    commands = CommandsHandler(config)
    Fire(commands)
