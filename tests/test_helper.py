from firestation_clustering.helper import get_nearby_fires


def test_get_nearby_fires():
    stations = [(50.0, 7.0), (51.0, 7.0), (50.0, 8.0), (51.0, 8.0)]
    fires = [(50.2, 7.0), (51.2, 7.0), (50.0, 8.2), (50.5, 8.0)]

    expected = [[(50.2, 7.0)], [(51.2, 7.0)], [(50.0, 8.2)], [(50.5, 8.0)]]

    actual = get_nearby_fires(stations, fires)

    assert len(expected) == len(actual)
    assert expected == actual
