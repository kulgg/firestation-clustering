from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class Distance:
    is_haversine: bool
    d: int


@dataclass
class Station:
    coordinates: Tuple[float, float]
    nearby_fires: List[Tuple[float, float]]
    distance: Distance


@dataclass
class Iteration:
    stations: List[Station]
    average_distance: Distance


@dataclass
class Results:
    iterations: List[Iteration]
