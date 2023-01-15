from math import sqrt
from typing import List, Tuple


def get_closest_station(fire, stations):
    best, i = 10000000000000, 0
    for j in range(len(stations)):
        s = stations[j]
        distance = sqrt(abs(fire[0] - s[0]) ** 2 + abs(fire[1] - s[1]) ** 2)
        if distance <= best:
            best = distance
            i = j

    return i


def get_nearby_fires(
    stations: List[Tuple[float, float]], fires: List[Tuple[float, float]]
) -> List[List[Tuple[float, float]]]:
    nearby_fires = [[] for _ in range(len(stations))]

    for f in fires:
        closest_station_index = get_closest_station(f, stations)
        nearby_fires[closest_station_index].append(f)

    return nearby_fires
