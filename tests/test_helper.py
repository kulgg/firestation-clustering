from firestation_clustering.helper import (
    get_average_distances,
    get_centers,
    get_nearby_fires,
)


def test_get_nearby_fires():
    stations = [(50.0, 7.0), (51.0, 7.0), (50.0, 8.0), (51.0, 8.0)]
    fires = [(50.2, 7.0), (51.2, 7.0), (50.0, 8.2), (50.5, 8.0)]

    expected = [[(50.2, 7.0)], [(51.2, 7.0)], [(50.0, 8.2)], [(50.5, 8.0)]]

    actual = get_nearby_fires(stations, fires, True)

    assert len(expected) == len(actual)
    assert expected == actual


def test_get_average_distance():
    stations = [(50.0, 7.0), (51.0, 7.0), (50.0, 8.0), (51.0, 8.0)]
    nearby_fires = [[(50.2, 7.0)], [(51.2, 7.0)], [(50.0, 8.2)], [(50.5, 8.0)]]

    assert [
        22.239016046706613,
        22.239016046706613,
        14.294959707570287,
        55.59754011676653,
    ] == get_average_distances(stations, nearby_fires, True)


def test_get_centers():
    stations = [(50.0, 7.0), (51.0, 7.0), (50.0, 8.0), (51.0, 8.0)]
    nearby_fires = [[(50.2, 7.0)], [(51.2, 7.0)], [(50.0, 8.2)], [(50.5, 8.0)]]

    expected = [(50.1, 7.0), (51.1, 7.0), (50.0, 8.1), (50.75, 8.0)]

    assert expected == get_centers(stations, nearby_fires)
