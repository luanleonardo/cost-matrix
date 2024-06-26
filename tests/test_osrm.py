import numpy as np
import pytest
from mock import patch
from requests import Response
from requests.exceptions import HTTPError

import cost_matrix as cm

OSRM_CALL_PATH = "cost_matrix.osrm_matrix.requests.get"


@pytest.fixture
def mocked_osrm_valid_call():
    with patch(OSRM_CALL_PATH) as (mocked_get):
        mocked_return_value = Response()
        mocked_return_value.status_code = 200
        mocked_return_value.json = lambda: {
            "code": "Ok",
            "distances": np.array([[0, 50], [50, 0]]),
            "durations": np.array([[0, 5], [5, 0]]),
        }
        mocked_get.return_value = mocked_return_value

        yield mocked_get


@pytest.fixture
def mocked_osrm_invalid_call():
    """It happens when no service is working or the input is invalid"""
    with patch(OSRM_CALL_PATH) as (mocked_get):
        mocked_return_value = Response()
        mocked_return_value.status_code = 400
        mocked_get.return_value = mocked_return_value

        yield mocked_get


@pytest.mark.usefixtures("mocked_osrm_valid_call")
def test_osrm_distance_valid_call():

    sources = np.array([[0.0, 0.0], [1.0, 1.0]])

    cost_matrix = cm.osrm(sources=sources, destinations=sources)

    num_sources = sources.shape[0]
    assert cost_matrix.shape == (num_sources, num_sources)


@pytest.mark.usefixtures("mocked_osrm_invalid_call")
def test_osrm_distance_invalid_call():

    sources = np.array([[0.0, 0.0], [1.0, 1.0]])

    with pytest.raises(HTTPError):
        cm.osrm(sources=sources, destinations=sources)


def test_osrm_distance_call_square_matrix(mocked_osrm_valid_call):

    sources = np.array([[0.0, 0.0], [1.0, 1.0]])
    server_address = "BASE_URL"

    cm.osrm(
        sources=sources,
        destinations=sources,
        server_address=server_address,
        cost_type="distances",
    )

    expected_url_call = (
        f"{server_address}/table/v1/driving/"
        f"0.0,0.0;1.0,1.0"
        "?annotations=distance"
    )

    mocked_osrm_valid_call.assert_called_with(expected_url_call)


def test_osrm_distance_call_non_square_matrix(mocked_osrm_valid_call):

    sources = np.array([[0.0, 0.0], [1.0, 1.0]])
    destinations = np.array([[2.0, 2.0], [3.0, 3.0]])
    server_address = "BASE_URL"

    cm.osrm(
        sources=sources,
        destinations=destinations,
        server_address=server_address,
        cost_type="distances",
    )

    expected_url_call = (
        f"{server_address}/table/v1/driving/"
        f"0.0,0.0;1.0,1.0;2.0,2.0;3.0,3.0"
        "?sources=0;1&destinations=2;3&annotations=distance"
    )

    mocked_osrm_valid_call.assert_called_with(expected_url_call)


def test_osrm_distance_call_durations_cost(mocked_osrm_valid_call):
    """Check if the URL is changed when the cost type is different"""

    sources = np.array([[0.0, 0.0], [1.0, 1.0]])
    server_address = "BASE_URL"

    cm.osrm(
        sources=sources,
        destinations=sources,
        server_address=server_address,
        cost_type="durations",
    )

    expected_url_call = (
        f"{server_address}/table/v1/driving/"
        f"0.0,0.0;1.0,1.0"
        "?annotations=duration"
    )

    mocked_osrm_valid_call.assert_called_with(expected_url_call)
