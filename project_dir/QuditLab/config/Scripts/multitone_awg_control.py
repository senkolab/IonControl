import matlab.engine
import numpy as np

# start the matplab engine
eng = matlab.engine.start_matlab()
eng.addpath(r'C:\Users\classicion\Documents\MATLAB\iqtools', nargout=0)

def initialize_awg(amplitude=3):
    eng.SendAWGCommand("RES", nargout=0)
    eng.SendAWGCommand("TRAC:DEL:ALL", nargout=0)
    eng.SendAWGCommand("SOUR:SEQ:DEL:ALL", nargout=0)
    eng.SendAWGCommand("SOUR:FUNC:MODE USER", nargout=0)
    eng.SendAWGCommand("ROSC:SOUR INT", nargout=0)
    eng.SendAWGCommand("OUTP:COUP DC", nargout=0)
    eng.SendAWGCommand(f"SOUR:VOLT:LEV:AMPL {amplitude}", nargout=0)
    eng.SendAWGCommand("INIT:CONT 1", nargout=0)

def upload_waveform_to_awg(signal, sample_rate, sequence_id=1, repetitions=3, normalize=False):
    eng.iqdownload(signal, sample_rate, 'sequence', matlab.double(sequence_id), "normalize", int(normalize), nargout=0)
    for i in range(1, repetitions + 1):
        eng.SendAWGCommand(f"SOUR:SEQ:DEF {i},{sequence_id},1,1", nargout=0)

    eng.SendAWGCommand("SOUR:FUNC:MODE SEQ", nargout=0)
    eng.SendAWGCommand("OUTP:STAT 1", nargout=0)

def make_multitone_waveform(frequencies, voltages, phases, pulse_length, sample_rate, scale=1, fix_sample_rate=True):
    """Create a multitone waveform with multiple frequencies at different amplitudes and phases."""
    if not (0 <= scale <= 1):
        raise ValueError(f"Scale must be a value in [0, 1], received {scale}")
    if fix_sample_rate:
        sample_rate = adjust_sample_rate(sample_rate, pulse_length)
    number_of_samples = pulse_length * sample_rate
    waveform = np.zeros(int(number_of_samples))
    times = np.arange(int(number_of_samples)) / sample_rate

    for freq, volt, phase in zip(frequencies, voltages, phases):
        waveform += volt * np.sin(2 * np.pi * freq * times + phase)
    waveform *= scale

    return waveform, sample_rate

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

frequencies = [610.418e6] # Hz
voltages = [1, 0] # V
phases = [0] # rad
pulse_length = 1000 / frequencies[0] # s
sample_rate = 4e9 # Hz
scale = 3

signal, sample_rate = make_multitone_waveform(frequencies, voltages, phases, pulse_length, sample_rate, scale=1 / scale)

try:
    initialize_awg()
    upload_waveform_to_awg(signal, sample_rate)
finally:
    eng.quit()
