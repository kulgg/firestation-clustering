import logging
from typing import Tuple, List
import requests
import urllib.parse


class MapBox:
    def __init__(self, token):
        self.token = token

    def distance_matrix(self, coordinates: List[Tuple[float, float]]):
        params = (
            (
                "access_token",
                self.token,
            ),
        )

        coordinates = ";".join([f"{t[0]},{t[1]}" for t in coordinates])

        response = requests.get(
            f"https://api.mapbox.com/directions-matrix/v1/mapbox/driving/{coordinates}",
            params=params,
        )

        return response.json()

    def static_map(
        self,
        center: Tuple[float, float],
        fires: List[Tuple[float, float]] = [],
        stations: List[Tuple[float, float]] = [],
        zoom=14,
        bearing=0,
        pitch=60,
        width=400,
        height=400,
    ):
        params = {
            "access_token": self.token,
        }
        
        markers = '{"type":"Point","coordinates":[7.154114,51.521568]}'
        
        url = f"https://api.mapbox.com/styles/v1/mapbox/streets-v12/static/geojson({urllib.parse.quote(markers)})/{center[1]},{center[0]},{zoom},{bearing},{pitch}/{width}x{height}",
        logging.info(url)

        response = requests.get(url, params=params)

        return response.content
