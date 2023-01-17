# Firestation Clustering

## How to run

1. Install https://python-poetry.org/docs/
2. Copy config-example.yaml to config.yaml
3. Insert api-key in config.yaml
4. `poetry install`
5. `poetry run x`

## ToDo

- [x] Switch everything to mapbox
- [x] Probabilistic fire spawning
- [x] Log all relevant data in every iteration
  - Firestation locations
  - Fire locations
  - Driving times /euclid distance
- [x] Add kmeans_driving_time results output
- [x] Run experiments
- [x] Calculate final average driving time for all experiments

## Experiments

- euclid uniform
- euclid weighted probabilities
- haversine uniform
- haversine weighted probabilities
- driving_time uniform
- driving_time weighted probabilities

Let's assume we have 1000 fires for the final metric.
How many matrix elements do we need?
-> `1000 * 4 * 6 = 24000`

For driving_time training we need
-> `2 * 20 * 400 * 4 = 64000`

Total matrix elements: `88000`
