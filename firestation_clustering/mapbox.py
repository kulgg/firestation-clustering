from typing import Tuple, List
import requests


class MapBox:
    def __init__(self):
        pass

    def distance_matrix(self, coordinates: List[Tuple[int, int]]):
        params = (
            (
                "access_token",
                "pk.eyJ1IjoiZ2x5Y2luY2hlY2siLCJhIjoiY2xjdDFvdDlhMHN4MzNwcDN5bzQ2d3lseiJ9.s4tYQvLfT1eNafvNwsQ5Mw",
            ),
        )

        coordinates = ";".join([f"{t[0]},{t[1]}" for t in coordinates])

        response = requests.get(
            f"https://api.mapbox.com/directions-matrix/v1/mapbox/driving/{coordinates}",
            params=params,
        )

        return response.json()
