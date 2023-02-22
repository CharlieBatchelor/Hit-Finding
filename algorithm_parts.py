# Find and return the frugal pedestal of the raw waveform. This corresponds to
# an adapting pedestal along the waveform, of size waveform.size
def frugal_pedestal(waveform, ncontig):
    # Initialise the median to be the first value t0 adc0 of the waveform
    median = waveform[0]
    ped = []
    running_diff = 0
    for i, s in enumerate(waveform):
        median, running_diff = do_frugal_update(median, running_diff, s, ncontig)
        ped.append(median)
    return ped


# Can implement this later
def frugal_pedestal_sigkill(waveform):
    return frugal_pedestal(waveform)


# Updates the median and running difference values, if a waveform
# is staying above pedestal for ncontig samples, then up the median!
def do_frugal_update(median, running_diff, s, ncontig):
    if s > median: running_diff += 1
    if s < median: running_diff -= 1
    if running_diff > ncontig:
        median += 1
        running_diff = 0
    if running_diff < -ncontig:
        median -= 1
        running_diff = 0
    return median, running_diff


# Filtering functions - Finite Impulse Response filtering
def apply_fir_filter(pedsub, ntaps, taps):
    filtered = [0]*len(pedsub)

    # Do the filtering...
    for i, s in enumerate(pedsub):
        for j, t in enumerate(taps):
            if i > j: index = i - j
            else: index = 0
            filtered[i] += pedsub[index]*taps[j]

    return filtered



