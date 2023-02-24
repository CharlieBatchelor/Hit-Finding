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


# Write the found TPs to a txt file
def write_tps_to_file(file, hits):
    f = open(file, "w")
    for hit_list in hits:
        for hit in hit_list:
            info = str(hit.start_time) + " " + str(hit.time_over_threshold) + " " + \
                   str(hit.peak_time) + " " + str(hit.channel) + " " + str(int(hit.sum_charge)) + " " + \
                   str(int(hit.peak_charge)) + " " + str(hit.det_id) + " " + str(hit.type) + "\n"

            f.write(info)
    f.close()