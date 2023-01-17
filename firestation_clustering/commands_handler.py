from time import sleep
import json
import logging
import os
import statistics
from firestation_clustering.mapbox import MapBox
from firestation_clustering.maps import Maps
from firestation_clustering.results import Iteration, Results, Station
from firestation_clustering.json_encoder import EnhancedJsonEncoder
from firestation_clustering.helper import (
    get_average_distances,
    get_centers,
    get_nearby_fires,
)


def chunker(seq, size):
    return (seq[pos : pos + size] for pos in range(0, len(seq), size))


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


class CommandsHandler:
    def __init__(self, config):
        self.config = config

    def avg_driving_duration(self, weighted_probabilities: bool):
        fires_fn = (
            "fires_uniform.txt" if not weighted_probabilities else "fires_weighted.txt"
        )
        fires_fd = open(f"{self.config['out-dir']}/fires_metric/{fires_fn}", "r")
        fires = [
            tuple(map(float, line.split(","))) for line in fires_fd.read().splitlines()
        ]
        fires_fd.close()

        stations = [
            (51.491289419753606, 7.168785569142202),
            (51.513886508587774, 7.244975565572561),
            (51.47095676026824, 7.262863693913191),
            (51.45053508209907, 7.149948683900617),
        ]
        logging.info("Driving time weighted")
        logging.info(len(fires))

        maps = Maps(self.config)

        driving_time = []
        for chunk in chunker(fires, 25 - len(stations)):
            driving_time.extend(maps.get_driving_time_matrix(chunk, stations))
            sleep(1)
            logging.info(len(driving_time))

        nearby_fires = [[] for i in range(len(stations))]
        driving_durations = [[] for i in range(len(stations))]
        for i in range(len(driving_time)):
            fire_to_stations_time = driving_time[i]
            driving_duration = min(fire_to_stations_time)
            nearest_index = fire_to_stations_time.index(driving_duration)
            nearby_fires[nearest_index].append(fires[i])
            driving_durations[nearest_index].append(driving_duration)

        for i in range(len(stations)):
            if not driving_durations[i]:
                driving_durations[i].append(0)

        avg_driving_durations = [statistics.mean(x) for x in driving_durations]
        logging.info(f"Average driving duration per station {avg_driving_durations}")
        overall_avg_driving_duration = statistics.mean(avg_driving_durations)
        logging.info(
            "Overall average driving duration %f", overall_avg_driving_duration
        )

    def generate_fires(self, num_fires, weighted_probabilities=False):
        maps = Maps(self.config)
        with open(f"{self.config['out-dir']}/fires.txt", "w") as f:
            text = "\n".join(
                list(
                    map(
                        lambda x: f"{x[0]},{x[1]},#FF0000,marker",
                        [
                            maps.get_random_point()
                            if not weighted_probabilities
                            else maps.get_random_point_weighted_by_population()
                            for _ in range(num_fires)
                        ],
                    )
                )
            )
            f.write(text)

    def kmeans(
        self,
        weighted_probabilities=False,
        use_haversine=True,
        num_iterations=10,
        city="Bochum",
    ):
        maps = Maps(self.config)

        type_str = "haversine" if use_haversine else "euclid"

        city_dir_path = (
            f"{self.config['out-dir']}/{city}/{type_str}/{weighted_probabilities}"
        )
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

        fires_fn = (
            "fires_uniform.txt" if not weighted_probabilities else "fires_weighted.txt"
        )
        fires_fd = open(f"{self.config['out-dir']}/{fires_fn}", "r")
        fires = [
            tuple(map(float, line.split(","))) for line in fires_fd.read().splitlines()
        ]
        fires_fd.close()

        num_fires = len(fires)
        logging.info("Num iterations %d", num_iterations)
        logging.info("Num fires %d", num_fires)
        logging.info("Weighted %r", weighted_probabilities)
        logging.info("Use haversine %r", use_haversine)

        results = Results(
            [], type_str, weighted_probabilities, num_fires, num_iterations
        )

        for i in range(num_iterations):
            map_img = maps.get_city_map_with_fires_and_stations([], stations)
            output_image_to_path(f"{city_dir_path}/{i}.png", map_img)

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

        results_fp = open(f"{city_dir_path}/results.json", "w")
        json.dump(results, results_fp, cls=EnhancedJsonEncoder, sort_keys=True)
        results_fp.close()

    def kmeans_driving_time(
        self,
        weighted_probabilities=False,
        num_iterations=10,
        city="Bochum",
    ):
        maps = Maps(self.config)

        city_dir_path = (
            f"{self.config['out-dir']}/{city}/driving-time/{weighted_probabilities}"
        )
        if not os.path.exists(city_dir_path):
            os.makedirs(city_dir_path)

        stations = [
            (51.4735733, 7.1513713),
            (51.476891, 7.2019071),
            (51.4885055, 7.2962569),
            (51.4424334, 7.1891685),
        ]

        fires_fn = (
            "fires_uniform.txt" if not weighted_probabilities else "fires_weighted.txt"
        )
        fires_fd = open(f"{self.config['out-dir']}/{fires_fn}", "r")
        fires = [
            tuple(map(float, line.split(","))) for line in fires_fd.read().splitlines()
        ]
        fires_fd.close()

        num_fires = len(fires)
        logging.info("Num iterations %d", num_iterations)
        logging.info("Num fires %d", num_fires)
        logging.info("Weighted %r", weighted_probabilities)

        results = Results(
            [], "driving_time", weighted_probabilities, num_fires, num_iterations
        )

        for j in range(num_iterations):
            logging.info("Iteration %d", j)

            map_img = maps.get_city_map_with_fires_and_stations([], stations)
            output_image_to_path(f"{city_dir_path}/{j}.png", map_img)

            driving_time = []
            for chunk in chunker(fires, 25 - len(stations)):
                driving_time.extend(maps.get_driving_time_matrix(chunk, stations))
                sleep(1)

            nearby_fires = [[] for i in range(len(stations))]
            driving_durations = [[] for i in range(len(stations))]
            for i in range(len(driving_time)):
                fire_to_stations_time = driving_time[i]
                driving_duration = min(fire_to_stations_time)
                nearest_index = fire_to_stations_time.index(driving_duration)
                nearby_fires[nearest_index].append(fires[i])
                driving_durations[nearest_index].append(driving_duration)

            for i in range(len(stations)):
                if not driving_durations[i]:
                    driving_durations[i].append(0)

            logging.info(driving_durations)
            avg_driving_durations = [statistics.mean(x) for x in driving_durations]
            overall_avg_duration = statistics.mean(avg_driving_durations)

            results.iterations.append(
                Iteration(
                    average_distance=overall_avg_duration,
                    stations=[
                        Station(
                            coordinates=stations[k],
                            nearby_fires=nearby_fires[k],
                            distance=avg_driving_durations[k],
                        )
                        for k in range(len(stations))
                    ],
                )
            )

            for i in range(len(stations)):
                if len(nearby_fires[i]) == 0:
                    continue
                lat = 0
                lng = 0
                for fire in nearby_fires[i]:
                    lat += fire[0]
                    lng += fire[1]
                lat /= len(nearby_fires[i])
                lng /= len(nearby_fires[i])

                stations[i] = (lat, lng)

        results_fp = open(f"{city_dir_path}/results.json", "w")
        json.dump(results, results_fp, cls=EnhancedJsonEncoder, sort_keys=True)
        results_fp.close()
        #     potential_stations = [(lat, lng), stations[i], *nearby_fires[i]]
        #     logging.info("Len potential_stations %d", len(potential_stations))

        #     driving_time = []
        #     for ps in potential_stations:
        #         driving_time.append(
        #             maps.get_driving_time_matrix([ps, *potential_stations])[0]
        #         )
        #         sleep(0.1)

        #     assert len(driving_time) == len(potential_stations)
        #     driving_time = [
        #         statistics.mean(drive_times_from_station)
        #         for drive_times_from_station in driving_time
        #     ]
        #     best_mean_drive_time = min(driving_time)
        #     logging.info(best_mean_drive_time)
        #     best_station_index = driving_time.index(best_mean_drive_time)
        #     logging.info(best_station_index)
        #     stations[i] = potential_stations[best_station_index]

    def test(self):
        mb = MapBox(self.config["mapbox"]["token"])
        mb.distance_matrix(
            [(51.521568, 7.154114)], [(51.525568, 7.158114), (51.521568, 7.154114)]
        )
