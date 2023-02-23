# Simple hit class - has all the information to generate hits to play in DUNE DAQ
class Hit:
    def __init__(self, channel, start_time, peak_charge, sum_charge, time_over_threshold):
        self.channel = 0
        self.start_time = 0
        self.peak_charge = 0
        self.sum_charge = 0
        self.time_over_threshold = 0


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


# Returns a list/array down sampled representation of the original waveform
def down_sample(waveform, down_sample_factor):

    # Just return the original waveform for unit down_sample_factor
    if down_sample_factor == 1:
        return waveform

    # Otherwise, return every down_sample_factor-th element of the original waveform
    down_sampled_waveform = []
    for i in waveform[::down_sample_factor]:
        down_sampled_waveform.append(i)
    return down_sampled_waveform


# Returns a list/array of median values corresponding to a running baseline/pedestal
def find_pedestal(waveform, use_sigkill, frugal_ped_ncontig):
    if use_sigkill:
        ped = frugal_pedestal_sigkill(waveform)
    else:
        ped = frugal_pedestal(waveform, frugal_ped_ncontig)
    return ped


# Filter
def filter(pedsub, filter_taps, do_filtering):
    ntaps = len(filter_taps)
    taps = filter_taps

    # If we are doing filter, apply FIR (finite impulse response) filter:
    if do_filtering:
        return apply_fir_filter(pedsub, ntaps, taps)
    else:
        return pedsub


# Does the hit finding for specified channel and returns list of hits
def hit_finding(waveform, channel, down_sample_factor, threshold):
    is_hit = False
    was_hit = False
    hit = Hit(channel, 0, 0, 0, 0)
    hit_charge = []
    hits = []

    for i, s in enumerate(waveform):
        sample_time = i * down_sample_factor
        adc = s

        # Introduce ignorance of first ~100 ticks for pedestal to stabalise
        is_hit = adc > threshold
        if is_hit and not was_hit:
            # Starting a hit, set start time:
            hit_charge.append(adc)
            hit.start_time = sample_time
            hit.sum_charge = adc
            hit.time_over_threshold = down_sample_factor
        if is_hit and was_hit:
            # Continuing a hit, add stuff
            hit_charge.append(adc)
            hit.sum_charge += adc * down_sample_factor
            hit.time_over_threshold += down_sample_factor
        if not is_hit and was_hit:
            # The hit is finished, output it.
            hit.peak_charge = max(hit_charge)
            hits.append(hit)
            hit_charge.clear()
        was_hit = is_hit

    return hits

