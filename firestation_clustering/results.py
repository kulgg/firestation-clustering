from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class Station:
    coordinates: Tuple[float, float]
    nearby_fires: List[Tuple[float, float]]
    distance: float


@dataclass
class Iteration:
    stations: List[Station]
    average_distance: float


@dataclass
class Results:
    iterations: List[Iteration]
    experiment_type: str  # haversine, euclid, driving tim
    weighted_probabilities: bool  # Spawn fires with probabilities weighted by population
    num_fires: int
    num_iterations: int
