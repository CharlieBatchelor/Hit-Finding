# PDS Hit Finding Code ============================================
import matplotlib.pyplot as plt
import numpy as np
from algorithm_parts import *
from basic_simulation_testing import *

# Parameters ------------------------------------------------------
threshold = 5  # Hit finding threshold on ADC
down_sample_factor = 1  # Factor by which to reduce the information in waveform
frugal_ped_ncontig = 15  # Number of samples to consider before adjusting median in ped finding
use_sigkill = False  # Implement this later
do_filtering = True  # Boolean, for deciding whether we do filtering
filter_taps = [1, 3, 6, 9, 6, 3, 1]  # FIR Taps - Need tuning

# Basic simulation testing ----------------------------------------
n = 10000                       # Scale/size of simulated waveform
x = np.linspace(0, n, n)        # Default size of sim waveform
n_waveforms = 10                # Default number of waveforms to make
use_simulation = True           # Only doing simulation for now
plotting_waveform = 0           # Test waveform to plot relevant data


# Algorithm functions ---------------------------------------------
def print_config():
    print("\n === PDS HIT FINDING ===\n")  # Press ⌘F8 to toggle the breakpoint.
    print("Hit finding ADC threshold: ", threshold)
    print("Down-sample factor: ", down_sample_factor)
    print("Frugal N Contiguous: ", frugal_ped_ncontig)
    print("Use Signal Kill? ", use_sigkill)
    print("Using filtering: ", do_filtering)
    print("Filter taps: ", filter_taps)
    print()


# Returns a list/array down sampled representation of the original waveform
def down_sample(waveform):

    # Just return the original waveform for unit down_sample_factor
    if down_sample_factor == 1:
        return waveform

    # Otherwise, return every down_sample_factor-th element of the original waveform
    down_sampled_waveform = []
    for i in waveform[::down_sample_factor]:
        down_sampled_waveform.append(i)
    return down_sampled_waveform


# Returns a list/array of median values corresponding to a running baseline/pedestal
def find_pedestal(waveform):
    if use_sigkill:
        ped = frugal_pedestal_sigkill(waveform)
    else:
        ped = frugal_pedestal(waveform, frugal_ped_ncontig)
    return ped


# Filter
def filter(pedsub):
    ntaps = len(filter_taps)
    taps = filter_taps

    # If we are doing filter, apply FIR (finite impulse response) filter:
    if do_filtering:
        return apply_fir_filter(pedsub, ntaps, taps)
    else:
        return pedsub


# Simple hit class - has all the information to generate hits to play in DUNE DAQ
class Hit:
    def __init__(self, channel, start_time, peak_charge, sum_charge, time_over_threshold):
        self.channel = 0
        self.start_time = 0
        self.peak_charge = 0
        self.sum_charge = 0
        self.time_over_threshold = 0


# Does the hit finding for specified channel and returns list of hits
def hit_finding(waveform, channel):
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


# Supply a list of channels and a list of waveforms to find hits on
def find_hits(channels, samples):
    hits = []  # The creature we return
    print("Called 'find_hits()' with ", len(samples), " channels. First channel has ", len(samples[0]), " samples.")

    for i, s in enumerate(samples):
        og_waveform = s
        waveform = down_sample(og_waveform)
        pedestal = find_pedestal(waveform)
        pedsub = []
        for j, adc in enumerate(waveform):
            pedsub.append(adc - pedestal[j])

        filtered = filter(pedsub)
        hits.append(hit_finding(filtered, channels[i]))

    print("Hit finding complete, returning ", len(hits[0]), " hits for first channel.")
    print("Returning total of ", len(hits), " lists of hits, should be one for each channel.")
    return hits


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_config()
    print()

    # SIMULATED GENERIC WAVEFORMS =======================================
    if use_simulation:
        # Test waveform
        test_waveforms = []
        channels = []
        for i in range(0, n_waveforms):
            test_waveforms.append(sim_waveform(x))
            channels.append(i)

        hits = find_hits(channels, test_waveforms)
    # === TESTING Complete - Now plot a sample waveform and data ========
        plt.plot(test_waveforms[0], label="Example Simulated Waveform")
        plt.plot(find_pedestal(test_waveforms[0]), label="Found Pedestal")
        plt.title("Simulated Waveform Example")
        plt.xlabel("Relative Time Tick")
        plt.ylabel("Arbitrary ADC Value")
        plt.legend()
        plt.show()
