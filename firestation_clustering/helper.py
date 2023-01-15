from math import sqrt
import statistics
from typing import List, Tuple
from haversine import haversine


def get_distance(a, b, use_haversine):
    if use_haversine:
        return haversine(a, b)
    return sqrt(abs(a[0] - b[0]) ** 2 + abs(a[1] - b[1]) ** 2)


def get_closest_station(fire, stations, use_haversine):
    best, i = 10000000000000, 0
    for j in range(len(stations)):
        s = stations[j]
        distance = get_distance(fire, s, use_haversine)
        if distance <= best:
            best = distance
            i = j

    return i


def get_nearby_fires(
    stations: List[Tuple[float, float]], fires: List[Tuple[float, float]], use_haversine
) -> List[List[Tuple[float, float]]]:
    nearby_fires = [[] for _ in range(len(stations))]

    for f in fires:
        closest_station_index = get_closest_station(f, stations, use_haversine)
        nearby_fires[closest_station_index].append(f)

    return nearby_fires


def get_average_distances(stations, nearby_fires, use_haversine):
    return [
        statistics.mean(
            get_distance(f, stations[i], use_haversine) for f in nearby_fires[i]
        )
        for i in range(len(stations))
    ]


def get_centers(stations, nearby_fires):
    return [
        (
            statistics.mean(
                [stations[i][0], *list(map(lambda x: x[0], nearby_fires[i]))]
            ),
            statistics.mean(
                [stations[i][1], *list(map(lambda x: x[1], nearby_fires[i]))]
            ),
        )
        for i in range(len(stations))
    ]
