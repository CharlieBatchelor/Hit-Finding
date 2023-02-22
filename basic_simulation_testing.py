import numpy as np


# Generate a generic 'random walk' style waveform and use this for hit finding:
def sim_waveform(x):
    y = 0
    result = []
    for _ in x:
        result.append(y)
        y += np.random.normal(scale=1)
    return np.array(result)


# Generate a sinusoidal waveform
def sin_waveform(x):
    return np.sin(x) + np.random.normal(scale=1, size=len(x))