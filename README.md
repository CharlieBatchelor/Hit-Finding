# Hit-Finding

A generic hit finding application that currently accepts streams of raw ADC information for multiple channels, and does the following:

1. Reads in and downsamples the waveform(s) if required.
2. Does basic pedestal finding and subtraction on the raw waveform.
3. Applies a simple Finite-Impulse-Response (FIR) filter to the waveform.
4. The result of passing the raw waveform through the sequence above is passed to the `hit_finding()` function, which returns a list of hits for each channel.


**Basic Simulation Test**

The hit finder is desinged to be pulse shape independent, and is based on the LArSoft DUNE implementation for TPC hit finding. The attempt _there_ was to mimic the hit finding proceudure in the `readout` subsystem of the DUNE Data Acquisition System (DAQ). The basic simulation test will generate several waveforms of size O(10k) samples, of a 'random-walk' style and pass them through the full sequence above to check hits are being generated.

