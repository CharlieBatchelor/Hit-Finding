# PDS Hit Finding Code ============================================
import matplotlib.pyplot as plt
import numpy as np
from algorithm_parts import *
from basic_simulation_testing import *
import json

# Hit Finding Parameters -------------------------------------------
threshold = 100           # Hit finding threshold on ADC - Use IQR instead?
down_sample_factor = 1    # Factor by which to reduce the information in waveform
frugal_ped_ncontig = 3    # Number of samples to consider before adjusting median in ped finding
use_sigkill = False       # Implement this later
do_filtering = True       # Boolean, for deciding whether we do filter
use_iqr_threshold = True  # Use the interquartile range as threshold for hit finding
filter_taps = [1, 2, 6, 8, 6, 2, 1]  # FIR Taps - Need tuning

# Basic Simulation Testing Parameters ------------------------------
n = 500                         # Scale/size of simulated waveform
x = np.linspace(0, n, n)        # Default size of sim waveform
n_waveforms = 10                # Default number of waveforms to make
use_simulation = False          # Only doing simulation for now
plotting_waveform = 0           # Test waveform to plot relevant data
use_random_walk = True          # It's random walk or noisy sine wave

# Data Testing ----------------------------------------------------
use_data = True
num_forms = 100                   # Number of waveforms to run hit finding on
hit_type = 2                    # 0: unknown, 1: TPC, 2: PDS

# Plotting & Output Parameters ---------------------------------------------
plotting = False
fontsize = 20
write_out_tps = True
out_file = "output_tps.txt"

# Algorithm functions ---------------------------------------------
def print_config():
    print("\n === PDS HIT FINDING ===\n")  # Press ⌘F8 to toggle the breakpoint.
    print("Hit finding ADC threshold: ", threshold)
    print("Down-sample factor: ", down_sample_factor)
    print("Frugal N Contiguous: ", frugal_ped_ncontig)
    print("Use Signal Kill? ", use_sigkill)
    print("Using filtering: ", do_filtering)
    print("Filter taps: ", filter_taps)
    print("Type of threshold: ", type(threshold))
    print()


# Supply a list of channels and a list of waveforms to find hits on
def find_hits(channels, samples):
    hits = []  # The creature we return
    print("\nCalled 'find_hits()' with ", len(samples), " channels. First channel has ", len(samples[0]), " samples.")

    for i, s in enumerate(samples):
        og_waveform = s
        waveform = down_sample(og_waveform, down_sample_factor)
        pedestal = find_pedestal(waveform, use_sigkill, frugal_ped_ncontig)
        pedsub = []
        for j, adc in enumerate(waveform):
            pedsub.append(adc - pedestal[j])
        filtered = filter(pedsub, filter_taps, do_filtering)
        if use_iqr_threshold:
            pedestal = find_pedestal(waveform, use_sigkill, frugal_ped_ncontig)
            iqr_threshold = frugal_iqr(filtered, pedestal, frugal_ped_ncontig)

        hits.append(hit_finding(filtered, channels[i], down_sample_factor, iqr_threshold, hit_type))

    print("Hit finding complete, returning ", len(hits[0]), " hits for first channel.")
    print("Returning total of ", len(hits), " lists of hits, should be one for each channel.")
    return hits


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_config()
    print()

    # SIMULATED GENERIC WAVEFORMS =======================================
    if use_simulation:
        test_waveforms = []
        channels = []
        for i in range(0, n_waveforms):
            if use_random_walk:
                test_waveforms.append(sim_waveform(x))
            else:
                test_waveforms.append(sin_waveform(x))
            channels.append(i+1)

        # The heavy lifting is done here, find the hits.
        hits = find_hits(channels, test_waveforms)

        # Hit Finding Complete - Now plot a sample waveform and data =====
        # Do pedestal subtraction for sample waveform
        tw = test_waveforms[plotting_waveform]
        ped = find_pedestal(tw, use_sigkill, frugal_ped_ncontig)
        pedsub = []
        for j, adc in enumerate(tw):
            pedsub.append(adc - ped[j])

        plt.plot(tw, label="Raw Simulated Waveform")
        plt.plot(find_pedestal(tw, use_sigkill, frugal_ped_ncontig), label="Found Pedestal")
        plt.plot(pedsub, label="Pedestal Subtracted Waveform")
        plt.grid()
        plt.title("Simulated Waveform Example", fontweight='bold')
        plt.xlabel("Relative Time Tick", fontweight='bold')
        plt.ylabel("Arbitrary ADC Value", fontweight='bold')
        plt.legend()
        plt.show()

    # Data sample - We'd like to consider real waveforms instead.
    if use_data:
        # Read in DAPHNE data
        file = open('config.json')
        config = json.load(file)
        data_loc = config['data_location']
        out_loc = config['output_location']
        daphne_data = np.load(data_loc)
        print("Shape of full DAPHNE dataframe: ", daphne_data.shape)
        wfs = daphne_data[:num_forms]
        print("Shape of single DAPHNE waveform: ", wfs[0].shape)
        channels = [i+1 for i in range(len(wfs))]

        # Do the hit finding on these waveforms separately
        hits = find_hits(channels, wfs)

        if write_out_tps:
            file = out_loc + out_file
            write_tps_to_file(file, hits)



        # Plot some DAPHNE data
        if plotting:
            # Setup subplots
            fig, axs = plt.subplots(num_forms, 1, sharex=True, sharey=True)
            fig.supxlabel("Relative Time - Ticks", fontweight="bold", fontsize=fontsize-5)
            fig.supylabel("ADC Count", fontweight="bold", fontsize=fontsize-5)
            fig.suptitle("Raw DAPHNE Waveforms - PROCESSED_CALIB_WVFS_SC.npy", fontweight="bold", fontsize=fontsize)
            axs.ravel()

            for i in range(0, num_forms):
                pedestal = find_pedestal(wfs[i], use_sigkill, frugal_ped_ncontig)
                iqr = frugal_iqr(wfs[i], pedestal, frugal_ped_ncontig)
                pedsub = []
                for j, adc in enumerate(wfs[i]):
                    pedsub.append(adc - pedestal[j])
                filtered = filter(pedsub, filter_taps, do_filtering)
                filtered_pedestal = frugal_pedestal(filtered, frugal_ped_ncontig)
                iqr_filtered = frugal_iqr(filtered, filtered_pedestal, frugal_ped_ncontig)
                iqr_threshold = [i * 3 for i in iqr_filtered]

                label = "Raw Waveform: " + str(i+1)

                # axs[i].plot(wfs[i], label=label)
                # axs[i].plot(pedestal, label="Pedestal")
                # axs[i].plot(iqr, label="Running Inter Quartile Range ~ Threshold Estimate")
                axs[i].plot(filtered, label="Filtered")
                axs[i].plot(iqr_threshold, label="Filtered IQR Doubled - Hit threshold")
                axs[i].grid('both')
                axs[i].legend()
                # axs[i].set_xlabel("Relative Time Tick", fontweight='bold')
                # axs[i].set_ylabel("Arbitrary ADC Value", fontweight='bold')

            plt.show()

