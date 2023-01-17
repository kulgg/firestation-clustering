from typing import Tuple, List
import requests
from geojson import Feature, Point, FeatureCollection
import urllib


class MapBox:
    def __init__(self, token):
        self.token = token

    def distance_matrix(
        self,
        sources: List[Tuple[float, float]],
        destinations: List[Tuple[float, float]],
    ):
        params = (
            (
                "access_token",
                self.token,
            ),
        )

        coordinates = ";".join([f"{t[1]},{t[0]}" for t in [*sources, *destinations]])

        source_indeces = ";".join([str(i) for i in range(len(sources))])
        destination_indeces = ";".join(
            [str(len(sources) + i) for i in range(len(destinations))]
        )
        url = f"https://api.mapbox.com/directions-matrix/v1/mapbox/driving/{coordinates}?sources={source_indeces}&destinations={destination_indeces}"

        response = requests.get(
            url,
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

    def illustration_map(
        self,
        center: Tuple[float, float],
        existing: List[Tuple[float, float]] = [],
        euclid: List[Tuple[float, float]] = [],
        haversine: List[Tuple[float, float]] = [],
        driving_time: List[Tuple[float, float]] = [],
        driving_time_optimized: List[Tuple[float, float]] = [],
        zoom=14,
        bearing=0,
        pitch=60,
        width=400,
        height=400,
    ):
        params = {
            "access_token": self.token,
        }

        existing = [
            Feature(
                geometry=Point((s[1], s[0])),
                properties={"marker-symbol": "fire-station", "marker-color": "#8B2635"},
            )
            for s in existing
        ]
        euclid = [
            Feature(
                geometry=Point((s[1], s[0])),
                properties={"marker-symbol": "fire-station", "marker-color": "#FA003F"},
            )
            for s in euclid
        ]
        haversine = [
            Feature(
                geometry=Point((s[1], s[0])),
                properties={"marker-symbol": "fire-station", "marker-color": "#41EAD4"},
            )
            for s in haversine
        ]
        driving_time = [
            Feature(
                geometry=Point((s[1], s[0])),
                properties={"marker-symbol": "fire-station", "marker-color": "#125E8A"},
            )
            for s in driving_time
        ]
        driving_time_optimized = [
            Feature(
                geometry=Point((s[1], s[0])),
                properties={"marker-symbol": "fire-station", "marker-color": "#FF9F1C"},
            )
            for s in driving_time_optimized
        ]

        euclid.extend(haversine)
        euclid.extend(driving_time)
        euclid.extend(driving_time_optimized)
        euclid.extend(existing)
        feature_collection = FeatureCollection(euclid)
        # markers = 'geojson({"type":"MultiPoint","coordinates":[STATIONS]})'
        # markers = 'geojson({"type":"FeatureCollection","features":[{"type":"MultiPoint","coordinates":[STATIONS]},{"type":"MultiPoint","coordinates":[FIRES]}]})'

        markers = str(feature_collection)

        url = f"https://api.mapbox.com/styles/v1/mapbox/streets-v12/static/geojson({urllib.parse.quote(markers)})/{center[1]},{center[0]},{zoom},{bearing},{pitch}/{width}x{height}"

        response = requests.get(url, params=params)

        return response.content
