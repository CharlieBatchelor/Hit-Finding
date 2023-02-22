import numpy as np


# Generate a generic waveform and use this for hit finding:
def sim_waveform(x):
    y = 0
    result = []
    for _ in x:
        result.append(y)
        y += np.random.normal(scale=1)
    return np.array(result)