import numpy as np


def manhattan(sources: np.ndarray, destinations: np.ndarray) -> np.ndarray:
    return np.sum(np.abs(sources - destinations), axis=1)
