import logging
from typing import Tuple, List
import requests
from geojson import Feature, Point, FeatureCollection
import urllib


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

        stations = [
            Feature(
                geometry=Point((s[1], s[0])),
                properties={"marker-symbol": "fire-station", "marker-color": "#00FFFF"},
            )
            for s in stations
        ]
        fires = [
            Feature(
                geometry=Point((s[1], s[0])),
                properties={"marker-color": "#FF0000"},
            )
            for s in fires
        ]
        stations.extend(fires)
        feature_collection = FeatureCollection(stations)
        # markers = 'geojson({"type":"MultiPoint","coordinates":[STATIONS]})'
        # markers = 'geojson({"type":"FeatureCollection","features":[{"type":"MultiPoint","coordinates":[STATIONS]},{"type":"MultiPoint","coordinates":[FIRES]}]})'

        markers = str(feature_collection)

        url = f"https://api.mapbox.com/styles/v1/mapbox/streets-v12/static/geojson({urllib.parse.quote(markers)})/{center[1]},{center[0]},{zoom},{bearing},{pitch}/{width}x{height}"

        response = requests.get(url, params=params)

        return response.content
