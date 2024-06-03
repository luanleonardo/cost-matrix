from math import ceil

import numpy as np
import requests


def osrm(
    sources: np.ndarray,
    destinations: np.ndarray,
    server_address: str = "http://router.project-osrm.org",
    batch_size: int = 150,
    cost_type: str = "distances",
) -> np.ndarray:
    """
    Compute the OSRM cost matrix between sources and destinations

    Parameters
    ----------
    sources : np.ndarray
        Array of shape (n, d) containing the source points.
    destinations : np.ndarray
        Array of shape (m, d) containing the destination points.
    server_address : str
        Address of the OSRM server. Default is "http://router.project-osrm.org".
    batch_size : int
        Number of points to send in each request. Default is 150.
    cost_type : str
        Type of cost to be computed. Default is "distances". Options are
        "distances" and "durations".

    Returns
    -------
    np.ndarray
        OSRM cost matrix of shape (n, m).
    """

    num_sources = sources.shape[0]
    num_destinations = destinations.shape[0]
    cost_matrix = np.zeros((num_sources, num_destinations))

    num_batches_i = ceil(num_sources / batch_size)
    num_batches_j = ceil(num_destinations / batch_size)

    for i in range(num_batches_i):
        start_i = i * batch_size
        end_i = min((i + 1) * batch_size, num_sources)

        for j in range(num_batches_j):
            start_j = j * batch_size
            end_j = min((j + 1) * batch_size, num_destinations)
            sources_batch = sources[start_i:end_i]
            destinations_batch = destinations[start_j:end_j]

            cost_matrix[start_i:end_i, start_j:end_j] = (
                _get_batch_osrm_distance(
                    sources_batch,
                    destinations_batch,
                    server_address,
                    cost_type=cost_type,
                )
            )

    return cost_matrix


def _get_batch_osrm_distance(
    sources_batch: np.ndarray,
    destinations_batch: np.ndarray,
    server_address: str,
    cost_type: str,
):
    """Request the OSRM cost matrix for a given batch"""

    url = _format_osrm_url(
        sources_batch, destinations_batch, server_address, cost_type
    )
    resp = requests.get(url)
    resp.raise_for_status()

    return np.array(resp.json()[cost_type])


def _format_osrm_url(
    sources_batch: np.ndarray,
    destinations_batch: np.ndarray,
    server_address: str,
    cost_type: str,
) -> str:
    """Format OSRM url string with sources and destinations

    Notes
    -----
    Consider the N sources in the form
        (lat_src1, lgn_src1), (lat_src2, lgn_src2), ...

    and the M destinations in the form
        (lat_dest1, lgn_dest1), (lat_dest2, lgn_dest2), ...

    This function converts these properties in a URL of the form
        {OSRM_SERVER_ADDRESS}/table/v1/driving/
        lng_src1,lat_src1;lng_src2,lat_src2;...;lng_srcN,lat_srcN;
        lng_dest1,lat_dest1;lng_dest2,lat_dest2;...;lng_destM,lng_destM
        ?sources=0;1;...;N-1
        &destinations=N;N+1;...;N+M-1
        &annotations=distance

    In the simpler case when sources == destinations, the URL is simplified to
        {OSRM_SERVER_ADDRESS}/table/v1/driving/
        lng_src1,lat_src1;lng_src2,lat_src2;...;lng_srcN,lat_srcN
        ?annotations=distance

    Obs: Replace "distance" with "duration" if a time matrix is required
    Obs2: The matrix type follows the singular form in the URL (e.g.,
    "distance"), but the returned JSON follows the plural form (e.g.,
    "distances"). Thus, we ignore the last letter of the input type
    """

    url_cost_type = cost_type[:-1]
    sources_coord = ";".join(
        f"{source[1]},{source[0]}" for source in sources_batch
    )

    # If sources == destinations, return a simpler URL early. Notice it needs
    # at least two points, otherwise OSRM complains
    if (
        np.array_equal(sources_batch, destinations_batch)
        and sources_batch.shape[0] > 1
    ):
        return (
            f"{server_address}/table/v1/driving/"
            f"{sources_coord}"
            f"?annotations={url_cost_type}"
        )

    destinations_coord = ";".join(
        f"{destination[1]},{destination[0]}"
        for destination in destinations_batch
    )
    locations_coord = sources_coord + ";" + destinations_coord

    # Get indices of sources and destinations in the form
    # sources = 0,1,...,N' and destinations = N'+1,N'+2...N'+M'
    num_sources = sources_batch.shape[0]
    num_destinations = destinations_batch.shape[0]

    sources_indices = ";".join(str(index) for index in range(num_sources))
    destinations_indices = ";".join(
        str(index)
        for index in range(num_sources, num_sources + num_destinations)
    )

    return (
        f"{server_address}/table/v1/driving/"
        f"{locations_coord}"
        f"?sources={sources_indices}&destinations={destinations_indices}"
        f"&annotations={url_cost_type}"
    )
