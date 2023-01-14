import logging
import os
import statistics
from fire import Fire
import yaml
from sklearn.cluster import KMeans
from firestation_clustering.mapbox import MapBox

from firestation_clustering.maps import Maps


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


class CommandsHandler:
    def __init__(self, config):
        self.config = config

    def kmeans_euclid(self, city, num_stations, num_fires=100, iterations=10):
        maps = Maps(self.config)
        maps.set_city(city)

        city_dir_path = f"out/{city}/euclid"
        if not os.path.exists(city_dir_path):
            os.makedirs(city_dir_path)

        stations = [maps.get_random_point() for _ in range(num_stations)]

        for i in range(iterations):
            fires = [maps.get_random_point() for _ in range(num_fires)]

            map_img = maps.get_city_map_with_fires_and_stations(fires, stations)

            output_image_to_path(f"out/{city}/euclid/{i}.png", map_img)

            kmeans = KMeans(
                n_clusters=num_stations, init=stations, n_init=1, max_iter=1
            ).fit(fires)
            stations = kmeans.cluster_centers_

    def kmeans_driving_time(self, city, num_stations, num_fires=100, iterations=10):
        maps = Maps(self.config["gmaps"])
        maps.set_city(city)

        city_dir_path = f"out/{city}/driving-time"
        if not os.path.exists(city_dir_path):
            os.makedirs(city_dir_path)

        fire_stations = []
        for i in range(num_stations):
            lat, lng = maps.get_random_point()
            fire_stations.append((lat, lng))

        f_stations = open(f"out/{city}/driving-time/stations.txt", "w")
        fires = []
        for j in range(iterations):
            logging.info("Iteration %d", j)
            f_stations.write(f"Iteration {j}\n")
            f_stations.write(
                " ".join(f"{lat},{lng}" for lat, lng in fire_stations) + "\n\n"
            )

            map_img = maps.get_city_map_with_fires_and_stations(fires, fire_stations)
            with open(f"out/{city}/driving-time/{j}.png", "wb") as f:
                for chunk in map_img:
                    if chunk:
                        f.write(chunk)

            fires = []
            for _ in range(num_fires):
                lat, lng = maps.get_random_point()
                fires.append((lat, lng))

            # every row contains the driving time seconds to all fire stations for a fire
            num_fires_per_request = 100 // num_stations
            driving_time = []
            for chunk in chunker(fires, num_fires_per_request):
                driving_time.extend(maps.get_driving_time_matrix(chunk, fire_stations))

            # The nearby fires of all fire stations
            nearby_fires = [[] for i in range(num_stations)]
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

                potential_stations = [(lat, lng), fire_stations[i]]
                potential_stations.extend(nearby_fires[i])
                logging.info("Len potential_stations %d", len(potential_stations))

                num_per_request = 100 // len(potential_stations)
                driving_time = []
                for chunk in chunker(potential_stations, num_per_request):
                    tmp = [[] for _ in range(len(chunk))]
                    for chunk_two in chunker(potential_stations, num_per_request):
                        res = maps.get_driving_time_matrix(chunk, chunk_two)
                        for k in range(len(chunk)):
                            tmp[k].extend(res[k])
                    driving_time.extend(tmp)

                assert len(driving_time) == len(potential_stations)
                driving_time = [
                    statistics.mean(drive_times_from_station)
                    for drive_times_from_station in driving_time
                ]
                best_mean_drive_time = min(driving_time)
                logging.info(best_mean_drive_time)
                best_station_index = driving_time.index(best_mean_drive_time)
                logging.info(best_station_index)
                fire_stations[i] = potential_stations[best_station_index]
        f_stations.close()

    def test(self):
        mb = MapBox(self.config["mapbox"]["token"])
        maps = Maps(self.config)
        # coordinates = [(-122.42, 37.78), (-122.45, 37.91), (-122.48, 37.73)]
        # logging.info(maps.get_random_point_weighted_by_population())

        stations = [
            [51.410443, 7.102131],
            [51.521568, 7.154114],
            [51.505821, 7.102756],
            [51.532128, 7.232064],
            [51.504190, 7.254022],
            [51.475234, 7.185753],
            [51.478328, 7.120075],
        ]

        fires = [[51.472238, 7.185753]]

        output_image_to_path(
            "out/test.jpg",
            mb.static_map(
                maps.get_city_center(),
                stations=stations,
                fires=fires,
                width=1200,
                height=1200,
                bearing=0,
                pitch=0,
                zoom=12,
            ),
        )


# returns single map with spawned fires
# parameters: city_name is the name of the whole city, the district_population_info is a dict with key of district_name and value of population number
def get_fire_of_districts(self, number_of_fires) -> list:
    city_map = Maps(self.config)
    fire_locations = [
        city_map.get_random_point_weighted_by_population()
        for _ in range(number_of_fires)
    ]

    return fire_locations


def output_image_to_path(path: str, image) -> None:
    with open(path, "wb") as f:
        f.write(image)


def main():
    config = load_config()
    configure_logging()
    logging.info("Hello")

    if not os.path.exists("out"):
        os.makedirs("out")

    commands = CommandsHandler(config)
    Fire(commands)
