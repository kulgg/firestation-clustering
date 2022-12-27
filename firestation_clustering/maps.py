import logging
import googlemaps
from datetime import datetime


class Maps:
    def __init__(self, config):
        self.gmaps = googlemaps.Client(key=config["api-key"])

    def do(self):
        now = datetime.now()
        directions_result = self.gmaps.directions(
            "Sydney Town Hall", "Parramatta, NSW", mode="transit", departure_time=now
        )

        logging.info(directions_result)
