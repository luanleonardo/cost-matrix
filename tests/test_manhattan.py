import numpy as np

import cost_matrix


def test_manhattan_matrix():
    sources = np.array([[0, 0]])
    destinations = np.array([[0, 0], [3, 4]])

    manhattan_matrix = cost_matrix.manhattan(sources, destinations)

    expected_result = np.array(
        [[0, 7]]
    )  # Expected Manhattan distances: [0, 3+4=7]

    assert np.array_equal(manhattan_matrix, expected_result)
