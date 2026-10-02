"""Specify multitone waveforms and upload them to the AWG."""

from fractions import Fraction
from time import sleep

import numpy as np
import matlab.engine


def calculate_pulse_length_from_frequencies(frequencies, denominator_limit=1_000_000):
    """
    Calculate pulse length as the LCM of periods implied by frequencies.

    Assumes frequencies can be expressed as rational multiples of a base frequency.

    Args:
        frequencies: List of frequencies in Hz
        denominator_limit: Maximum denominator for rational approximation (default 1_000_000)

    Returns:
        pulse_length: Time duration (in seconds) equal to the lowest common multiple of the periods of all frequencies
    """
    base_freq = min(frequencies)
    ratios = [Fraction(f / base_freq).limit_denominator(denominator_limit) for f in frequencies]
    period_nums = np.array([r.denominator for r in ratios], dtype=np.int64)
    period_dens = np.array([r.numerator for r in ratios], dtype=np.int64)
    lcm_num = np.lcm.reduce(period_nums)
    gcd_den = np.gcd.reduce(period_dens)
    return (lcm_num / gcd_den) / base_freq
    

def adjust_sample_rate(sample_rate, pulse_duration, multiple=32, min_samples=384):
    """Adjust sample rate so that number of samples is a multiple of 'multiple'."""
    if min_samples % multiple != 0:
        raise ValueError("min_samples must be a multiple of 'multiple'")

    number_of_samples = pulse_duration * sample_rate
    remainder = number_of_samples % multiple
    if remainder != 0:
        adjusted_number_of_samples = number_of_samples + (multiple - remainder)
        if adjusted_number_of_samples < min_samples:
            adjusted_number_of_samples = min_samples

        adjusted_sample_rate = adjusted_number_of_samples / pulse_duration
        return adjusted_sample_rate
    return sample_rate
    

def make_multitone_waveform(frequencies, voltages, phases, pulse_length, sample_rate, scale=1, fix_sample_rate=True):
    """Create a multitone waveform with multiple frequencies at different amplitudes and phases."""
    if not (0 <= scale <= 1):
        raise ValueError(f"Scale must be a value in [0, 1], received {scale}")
    
    if not len(frequencies) == len(voltages) == len(phases):
        raise ValueError("Number of frequencies, voltages, and phases must be equal")

    if fix_sample_rate:
        sample_rate = adjust_sample_rate(sample_rate, pulse_length)
    number_of_samples = pulse_length * sample_rate
    waveform = np.zeros(int(number_of_samples))
    times = np.arange(int(number_of_samples)) / sample_rate

    for freq, volt, phase in zip(frequencies, voltages, phases):
        waveform += volt * np.sin(2 * np.pi * freq * times + phase)
    waveform *= scale

    return waveform, sample_rate


def _start_matlab_engine():
    """Start the MATLAB engine to enable communication with the AWG"""
    eng = matlab.engine.start_matlab()
    eng.addpath(r'C:\Users\ions\Documents\MATLAB\iqtools_old', nargout=0)
    return eng


eng = _start_matlab_engine()


def initialize_awg(amplitude=3, verbose=True):
    """
    Initialize Agilent 81180B AWG with error checking.

    Args:
        amplitude: Output amplitude in Volts (default 3)
        verbose: Print status messages (default True)
    """
    def log(msg):
        if verbose:
            print(msg)

    try:
        log("Initializing AWG...")
        log("  Sending RESET...")
        eng.SendAWGCommand("RES", nargout=0)
        sleep(0.5)

        log("  Clearing traces...")
        eng.SendAWGCommand("TRAC:DEL:ALL", nargout=0)
        sleep(0.2)

        log("  Clearing sequences...")
        eng.SendAWGCommand("SOUR:SEQ:DEL:ALL", nargout=0)
        sleep(0.2)

        log("  Setting function mode to USER...")
        eng.SendAWGCommand("SOUR:FUNC:MODE USER", nargout=0)
        sleep(0.1)

        log("  Setting internal clock source...")
        eng.SendAWGCommand("ROSC:SOUR INT", nargout=0)
        sleep(0.1)

        log("  Setting output coupling to DC...")
        eng.SendAWGCommand("OUTP:COUP DC", nargout=0)
        sleep(0.1)

        log(f"  Setting output amplitude to {amplitude} V...")
        eng.SendAWGCommand(f"SOUR:VOLT:LEV:AMPL {amplitude}", nargout=0)
        sleep(0.1)

        log("  Enabling continuous operation...")
        eng.SendAWGCommand("INIT:CONT 1", nargout=0)
        sleep(0.2)

        # Verify initialization
        # log("\nVerifying AWG configuration...")
        # try:
        #     identity = eng.SendAWGCommand('*IDN?', nargout=1)
        #     log(f"?? AWG identified: {identity}")
        # except Exception as e:
        #     log(f"?  Warning: Could not read AWG identity: {e}")

        # log("?? AWG initialization complete!\n")
        
    except Exception as e:
        log(f"\n?? ERROR during AWG initialization: {e}")
        log("\nTroubleshooting:")
        log("  1. Check that AWG is powered on and connected")
        log("  2. Verify MATLAB iqtools is in path:")
        log(f"     {eng.path(nargout=1)}")
        log("  3. Try restarting the MATLAB engine in the next cell")
        raise


def send_awg_command(command):
    return eng.SendAWGCommand(command, nargout=1)

def check_awg_connection():
    """Check if AWG is responding to commands."""
    try:
        result = eng.SendAWGCommand('*IDN?', nargout=1)
        print(f"?? AWG is responding: {result}")
        return True
    except Exception as e:
        print(f"?? AWG not responding: {e}")
        return False
        
        
def upload_waveform_to_awg(signal, sample_rate, sequence_id=1, repetitions=3, normalize=False):
    """
    Upload waveform to AWG with better error handling and robustness.

    Args:
        signal: Waveform data (numpy array)
        sample_rate: Sample rate in Hz
        sequence_id: Sequence table entry (default 1)
        repetitions: Number of sequence table repetitions (default 3)
        normalize: Auto-scale data to max DAC range (default True)
    """
    try:
        # # Verify AWG is responding before download
        # print("Checking AWG connection...")
        # try:
        #     status = eng.SendAWGCommand('*IDN?', nargout=1)
        #     print(f"?? AWG connected: {status}")
        # except Exception as e:
        #     print(f"?  Warning: Could not verify AWG connection: {e}")
        #     print("  Proceeding anyway, but connection may be lost...")
        check_awg_connection()
        
        # Convert numpy array to MATLAB format
        print(f"Preparing waveform (sample rate: {sample_rate / 1e9:.1f} GSa/s)...")
        if hasattr(signal, 'tolist'):
            signal = signal.tolist()
        else:
            signal = list(signal)

        # Download waveform
        print(f"Downloading waveform to AWG sequence {sequence_id}...")
        eng.iqdownload(matlab.double(signal),
                      matlab.double([sample_rate]),
                      'sequence',
                      matlab.double([sequence_id]),
                      'normalize',
                      matlab.double([normalize]),
                      nargout=0)
        sleep(0.5)  # Allow AWG to process

        # Configure sequence table
        print(f"Configuring {repetitions} sequence table entry(ies)...")
        for i in range(1, repetitions + 1):
            eng.SendAWGCommand(f"SOUR:SEQ:DEF {i},{sequence_id},1,1", nargout=0)
            sleep(0.1)

        # Enable sequence mode and output
        print("Enabling sequence mode...")
        eng.SendAWGCommand("SOUR:FUNC:MODE SEQ", nargout=0)
        sleep(0.1)

        print("Starting output...")
        eng.SendAWGCommand("OUTP:STAT 1", nargout=0)

        print("?? Waveform upload complete!")

    except Exception as e:
        print(f"\n?? ERROR during waveform upload: {e}")
        print("\nTroubleshooting steps:")
        print("  1. Check physical AWG connection")
        print("  2. Verify MATLAB iqtools paths are correct")
        print("  3. Try restart MATLAB engine (restart kernel)")
        print("\nAttempting to read AWG error register...")
        try:
            error_msg = eng.SendAWGCommand(':SYST:ERR?', nargout=1)
            print(f"  AWG System Error: {error_msg}")
        except Exception as e2:
            print(f"  Could not read error register: {e2}")
        raise