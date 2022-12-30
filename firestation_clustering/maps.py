import logging
import random
import googlemaps
from datetime import datetime
from dataclasses import dataclass


@dataclass
class Area:
    min_lat: float
    max_lat: float
    min_lng: float
    max_lng: float


class Maps:
    def __init__(self, config):
        self.gmaps = googlemaps.Client(key=config["api-key"])
        self.city = None

    def do(self):
        now = datetime.now()
        directions_result = self.gmaps.directions(
            "Sydney Town Hall", "Parramatta, NSW", mode="transit", departure_time=now
        )

        logging.info(directions_result)

    def set_city(self, city_name):
        geocode_result = self.gmaps.geocode(city_name)[0]
        bounds = geocode_result["geometry"]["bounds"]

        self.city = Area(
            min_lat=bounds["southwest"]["lat"],
            max_lat=bounds["northeast"]["lat"],
            min_lng=bounds["southwest"]["lng"],
            max_lng=bounds["northeast"]["lng"],
        )

    def get_random_point(self):
        lat = random.uniform(self.city.min_lat, self.city.max_lat)
        lng = random.uniform(self.city.min_lng, self.city.max_lng)

        return (lat, lng)
