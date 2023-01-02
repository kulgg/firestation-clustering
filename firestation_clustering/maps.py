import random
import googlemaps
from dataclasses import dataclass


@dataclass
class Area:
    min_lat: float
    max_lat: float
    min_lng: float
    max_lng: float


class Maps:
    def __init__(self, config):
        self.gmaps: googlemaps.Client = googlemaps.Client(key=config["api-key"])
        self.city = None
        self.prev_stations = []

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

    def get_city_map(self, fires, stations):
        center_lat = (self.city.min_lat + self.city.max_lat) / 2
        center_lng = (self.city.min_lng + self.city.max_lng) / 2

        fire_markers_string = "icon:https://i.ibb.co/8X2GjdL/fire.png|" + "|".join(
            f"{lat},{lng}" for lat, lng in fires
        )

        station_markers_string = "color:blue|label:N|" + "|".join(
            f"{lat},{lng}" for lat, lng in stations
        )

        prev_station_markers_string = "color:red|label:O|" + "|".join(
            f"{lat},{lng}" for lat, lng in self.prev_stations
        )

        markers_string = [station_markers_string, prev_station_markers_string]
        if len(markers_string) + len(fires) <= 150:
            markers_string.append(fire_markers_string)

        map_img = self.gmaps.static_map(
            center=f"{center_lat},{center_lng}",
            size=(1000, 1000),
            zoom=11.8,
            markers=markers_string,
        )

        self.prev_stations = [s for s in stations]

        return map_img

    def get_driving_time_matrix(self, origins, destinations):
        matrix = self.gmaps.distance_matrix(origins, destinations, mode="driving")

        driving_time = [
            [row["elements"][i]["duration"]["value"] for i in range(len(destinations))]
            for row in matrix["rows"]
        ]

        return driving_time
