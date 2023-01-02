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

    def kmeans_euclid(self, city, num_stations, num_fires=100, iterations=10):
        maps = Maps(self.config["gmaps"])
        maps.set_city(city)

        city_dir_path = f"out/{city}/euclid"
        if not os.path.exists(city_dir_path):
            os.makedirs(city_dir_path)

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

            with open(f"out/{city}/euclid/{i}.png", "wb") as f:
                for chunk in map_img:
                    if chunk:
                        f.write(chunk)

            kmeans = KMeans(
                n_clusters=num_stations, init=fire_stations, n_init=1, max_iter=1
            ).fit(fires)
            fire_stations = kmeans.cluster_centers_

    def kmeans_driving_time(self, city, num_stations, num_fires=10, iterations=10):
        maps = Maps(self.config["gmaps"])
        maps.set_city(city)

        city_dir_path = f"out/{city}/driving-time"
        if not os.path.exists(city_dir_path):
            os.makedirs(city_dir_path)

        fire_stations = []
        for i in range(num_stations):
            lat, lng = maps.get_random_point()
            fire_stations.append((lat, lng))

        # The nearby fires of all fire stations
        nearby_fires = [[] for i in range(num_stations)]

        for i in range(iterations):
            fires = []
            for _ in range(num_fires):
                lat, lng = maps.get_random_point()
                fires.append((lat, lng))

            # every row contains the driving time seconds to all fire stations for a fire
            driving_time = maps.get_driving_time_matrix(fires, fire_stations)
            map_img = maps.get_city_map(
                [fire for sub_list in nearby_fires for fire in sub_list], fire_stations
            )

            with open(f"out/{city}/driving-time/{i}.png", "wb") as f:
                for chunk in map_img:
                    if chunk:
                        f.write(chunk)

            for i in range(len(driving_time)):
                fire_to_stations_time = driving_time[i]
                nearest_index = fire_to_stations_time.index(min(fire_to_stations_time))
                nearby_fires[nearest_index].append(fires[i])

            for i in range(num_stations):
                if len(nearby_fires[i]) == 0:
                    continue
                lat = 0
                lng = 0
                for fire in nearby_fires[i]:
                    lat += fire[0]
                    lng += fire[1]
                lat /= len(nearby_fires[i])
                lng /= len(nearby_fires[i])
                fire_stations[i] = (lat, lng)


def main():
    config = load_config()
    configure_logging()
    logging.info("Hello")

    if not os.path.exists("out"):
        os.makedirs("out")

    commands = CommandsHandler(config)
    Fire(commands)
