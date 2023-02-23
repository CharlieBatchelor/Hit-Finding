# Simple hit class - has all the information to generate hits to play in DUNE DAQ
class Hit:
    def __init__(self, channel, start_time, peak_charge, sum_charge, time_over_threshold):
        self.channel = 0
        self.start_time = 0
        self.peak_charge = 0
        self.sum_charge = 0
        self.time_over_threshold = 0


# Class which matches the structure of a DUNE DAQ TP
class TP:
    def __init__(self, start_time, time_over_threshold, peak_time, channel, sum_charge, peak_charge, det_id, type):
        self.start_time = 0            # Start time
        self.time_over_threshold = 0   # Time over ADC threshold
        self.peak_time = 0             # Time of peak ADC value
        self.channel = 0               # Offline ADC Channel ID (Wire/Strip)
        self.sum_charge = 0            # ADC Integral of hit
        self.peak_charge = 0           # Highest ADC value of hit
        self.det_id = 0                # Detector Unit ID
        self.type = 0                  # 0:Unknown 1:TPC or 2:PDS


def frugal_iqr(waveform, pedestal, frugal_ncontig):
    iqr = [0]*len(waveform)

    rd_lo = 0
    rd_hi = 0
    q_lo = pedestal[0]-1
    q_hi = pedestal[0]+1

    for i, s in enumerate(waveform):
        if s < pedestal[i]:
            q_lo, rd_lo = do_frugal_update(q_lo, rd_lo, s, frugal_ncontig)
        if s > pedestal[i]:
            q_hi, rd_hi = do_frugal_update(q_hi, rd_hi, s, frugal_ncontig)

        iqr[i] = q_hi - q_lo

    return iqr


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
def hit_finding(waveform, channel, down_sample_factor, threshold, type):
    is_hit = False
    was_hit = False
    hit = Hit(channel, 0, 0, 0, 0)
    hit = TP(0, 0, 0, channel, 0, 0, 1, type)
    hit_charge = []
    hit_time = []
    hits = []

    for i, s in enumerate(waveform):
        sample_time = i * down_sample_factor
        adc = s

        # Ignore first 500 ticks for pedestal to stabalise
        if i < 500: continue

        # Introduce ignorance of first ~100 ticks for pedestal to stabalise
        is_hit = adc > 3*threshold[i]
        if is_hit and not was_hit:
            # Starting a hit, set start time:
            hit_charge.append(adc)
            hit_time.append(i)
            hit.start_time = sample_time
            hit.sum_charge = adc
            hit.time_over_threshold = down_sample_factor
        if is_hit and was_hit:
            # Continuing a hit, add stuff
            hit_charge.append(adc)
            hit_time.append(i)
            hit.sum_charge += adc * down_sample_factor
            hit.time_over_threshold += down_sample_factor
        if not is_hit and was_hit:
            # The hit is finished, output it.
            hit.peak_charge = max(hit_charge)
            hit.peak_time = hit_time[hit_charge.index(max(hit_charge))]
            hits.append(hit)
            hit_charge.clear()
            hit_time.clear()
        was_hit = is_hit

    return hits

