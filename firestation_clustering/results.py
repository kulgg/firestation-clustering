from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class Station:
    coordinates: Tuple[float, float]
    nearby_fires: List[Tuple[float, float]]
    euclid: List[float]


@dataclass
class Iteration:
    stations: List[Station]


@dataclass
class Results:
    iterations: List[Iteration]
