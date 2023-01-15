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
- [ ] Add kmeans_driving_time results output
- [ ] Run experiments
- [ ] Calculate final average driving time for all experiments
