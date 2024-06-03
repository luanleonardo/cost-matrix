import numpy as np


def euclidean(sources: np.ndarray, destinations: np.ndarray) -> np.ndarray:
    return np.linalg.norm(sources - destinations, axis=1)
