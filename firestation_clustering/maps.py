import random
from typing import List
from dataclasses import dataclass
from numpy.random import choice

from firestation_clustering.mapbox import MapBox


@dataclass
class Area:
    min_lat: float
    max_lat: float
    min_lng: float
    max_lng: float


class Maps:
    def __init__(self, config):
        self.mb = MapBox(config["mapbox"]["token"])
        self.city = Area(51.410443, 51.531295, 7.102131, 7.349272)

        # 1 "Bochum-Mitte": 103918,
        # 2 "Bochum-Wattenscheid": 72821,
        # 3 "Bochum-Nord": 35458,
        # 4 "Bochum-Ost": 52885,
        # 5 "Bochum-Süd": 50612,
        # 6 "Bochum-Südwest": 54452,
        # totale anzahl in bochum = 370.146

        self.district_locations: List[Area] = [
            Area(51.457411, 51.521568, 7.154114, 7.266257),
            Area(51.436690, 51.505821, 7.102756, 7.180607),
            Area(51.481955, 51.532128, 7.232064, 7.316238),
            Area(51.457872, 51.504190, 7.254022, 7.348968),
            Area(51.412156, 51.475234, 7.185753, 7.298447),
            Area(51.412594, 51.478328, 7.120075, 7.217956),
        ]
        self.district_probabilites = [0.28, 0.20, 0.10, 0.14, 0.13, 0.15]

    def get_city_center(self):
        center_lat = (self.city.min_lat + self.city.max_lat) / 2
        center_lng = (self.city.min_lng + self.city.max_lng) / 2
        center = [center_lat, center_lng]
        return center

    def get_random_point(self):
        lat = random.uniform(self.city.min_lat, self.city.max_lat)
        lng = random.uniform(self.city.min_lng, self.city.max_lng)

        return (lat, lng)

    def get_random_point_weighted_by_population(self):
        index_of_chosen_district = choice(
            [0, 1, 2, 3, 4, 5], 1, p=self.district_probabilites
        )[0]

        lat = random.uniform(
            self.district_locations[index_of_chosen_district].min_lat,
            self.district_locations[index_of_chosen_district].max_lat,
        )
        long = random.uniform(
            self.district_locations[index_of_chosen_district].min_lng,
            self.district_locations[index_of_chosen_district].max_lng,
        )

        return (lat, long)

    def get_city_map_with_fires_and_stations(self, fires, stations):
        map_img = self.mb.static_map(
            center=self.get_city_center(),
            fires=fires,
            stations=stations,
            width=1200,
            height=1200,
            zoom=11.8,
            pitch=0,
        )

        return map_img

    def get_city_map(self):
        center = self.get_city_center()
        map_img = self.mb.static_map(center, width=1200, height=1200, pitch=0)

        return map_img

    def get_driving_time_matrix(self, sources, destinations):
        matrix = self.mb.distance_matrix(sources, destinations)

        return matrix["durations"]
