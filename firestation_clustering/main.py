import json
import logging
import os
import statistics
from time import sleep
from fire import Fire
import yaml
from firestation_clustering.helper import (
    get_average_distances,
    get_centers,
    get_nearby_fires,
)
from firestation_clustering.json_encoder import EnhancedJsonEncoder
from firestation_clustering.mapbox import MapBox

from firestation_clustering.maps import Maps
from firestation_clustering.results import Iteration, Results, Station


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

    def kmeans(
        self,
        weighted_probabilities=False,
        use_haversine=True,
        num_fires=100,
        num_iterations=10,
        city="Bochum",
    ):
        maps = Maps(self.config)

        type_str = "haversine" if use_haversine else "euclid"

        city_dir_path = f"out/{city}/{type_str}/{weighted_probabilities}"
        if not os.path.exists(city_dir_path):
            os.makedirs(city_dir_path)

        # Actual stations
        # Grünstraße 31
        # Bessemerstraße 26
        # Brandwacht 1
        # Hattinger Straße 410
        stations = [
            (51.4735733, 7.1513713),
            (51.476891, 7.2019071),
            (51.4885055, 7.2962569),
            (51.4424334, 7.1891685),
        ]

        results = Results(
            [], type_str, weighted_probabilities, num_fires, num_iterations
        )

        for i in range(num_iterations):
            fires = [
                maps.get_random_point()
                if not weighted_probabilities
                else maps.get_random_point_weighted_by_population()
                for _ in range(num_fires)
            ]

            # map_img = maps.get_city_map_with_fires_and_stations([], stations)

            # output_image_to_path(f"{city_dir_path}/{i}.png", map_img)
            fires_near_stations = get_nearby_fires(stations, fires, use_haversine)
            avg_distance_to_fires = get_average_distances(
                stations, fires_near_stations, use_haversine
            )
            overall_avg_distance = statistics.mean(avg_distance_to_fires)
            logging.info(overall_avg_distance)

            results.iterations.append(
                Iteration(
                    average_distance=overall_avg_distance,
                    stations=[
                        Station(
                            coordinates=stations[j],
                            nearby_fires=fires_near_stations[j],
                            distance=avg_distance_to_fires[j],
                        )
                        for j in range(len(stations))
                    ],
                )
            )
            stations = get_centers(stations, fires_near_stations)

        results.iterations.append(
            Iteration(
                average_distance=overall_avg_distance,
                stations=[
                    Station(
                        coordinates=stations[j],
                        nearby_fires=fires_near_stations[j],
                        distance=avg_distance_to_fires[j],
                    )
                    for j in range(len(stations))
                ],
            )
        )
        results_fp = open(f"{city_dir_path}/results.json", "w")
        json.dump(results, results_fp, cls=EnhancedJsonEncoder, sort_keys=True)
        results_fp.close()

    def kmeans_driving_time(
        self,
        num_stations,
        weighted_probabilities=False,
        num_fires=100,
        iterations=10,
        city="Bochum",
    ):
        maps = Maps(self.config)

        city_dir_path = f"out/{city}/driving-time"
        if not os.path.exists(city_dir_path):
            os.makedirs(city_dir_path)

        stations = [maps.get_random_point() for _ in range(num_stations)]

        f_stations = open(f"out/{city}/driving-time/stations.txt", "w")
        fires = []
        for j in range(iterations):
            logging.info("Iteration %d", j)
            f_stations.write(f"Iteration {j}\n")
            f_stations.write(" ".join(f"{lat},{lng}" for lat, lng in stations) + "\n\n")

            map_img = maps.get_city_map_with_fires_and_stations(fires, stations)
            output_image_to_path(f"out/{city}/driving-time/{j}.png", map_img)

            fires = [
                maps.get_random_point()
                if not weighted_probabilities
                else maps.get_random_point_weighted_by_population()
                for _ in range(num_fires)
            ]

            # every row contains the driving time seconds to all fire stations for a fire
            driving_time = []
            # for chunk in chunker(fires, num_fires_per_request):
            for fire in fires:
                driving_time.append(maps.get_driving_time_matrix([fire, *stations])[0])
                sleep(0.1)

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

                potential_stations = [(lat, lng), stations[i], *nearby_fires[i]]
                logging.info("Len potential_stations %d", len(potential_stations))

                driving_time = []
                for ps in potential_stations:
                    driving_time.append(
                        maps.get_driving_time_matrix([ps, *potential_stations])[0]
                    )
                    sleep(0.1)

                assert len(driving_time) == len(potential_stations)
                driving_time = [
                    statistics.mean(drive_times_from_station)
                    for drive_times_from_station in driving_time
                ]
                best_mean_drive_time = min(driving_time)
                logging.info(best_mean_drive_time)
                best_station_index = driving_time.index(best_mean_drive_time)
                logging.info(best_station_index)
                stations[i] = potential_stations[best_station_index]
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
