import statistics
from typing import List, Tuple
from haversine import haversine


def get_distance(a, b):
    # return sqrt(abs(a[0] - b[0]) ** 2 + abs(a[1] - b[1]) ** 2)
    return haversine(a, b)


def get_closest_station(fire, stations):
    best, i = 10000000000000, 0
    for j in range(len(stations)):
        s = stations[j]
        distance = get_distance(fire, s)
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


def get_average_distance(stations, nearby_fires):
    return [
        statistics.mean(get_distance(f, stations[i]) for f in nearby_fires[i])
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
