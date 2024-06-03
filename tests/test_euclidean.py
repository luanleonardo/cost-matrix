import numpy as np

import cost_matrix


def test_euclidean_matrix():
    sources = np.array([[0, 0]])
    destinations = np.array([[0, 0], [3, 4]])

    euclidean_matrix = cost_matrix.euclidean(sources, destinations)

    expected_result = np.array(
        [[0.0, 5.0]]
    )  # Expected Euclidean distances: [0.0, sqrt(3^2 + 4^2) = 5.0]

    assert np.array_equal(euclidean_matrix, expected_result)
