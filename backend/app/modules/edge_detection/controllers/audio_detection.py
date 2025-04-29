import numpy as np
import scipy.io.wavfile as wav

def load_audio(filename):
    sample_rate, data = wav.read(filename)
    # If stereo, take only one channel
    if len(data.shape) == 2:
        data = data[:, 0]
    return sample_rate, data

def frame_audio(data, sample_rate, frame_duration_ms=10):
    frame_size = int(sample_rate * (frame_duration_ms / 1000))
    hop_size = frame_size
    frames = []
    for start in range(0, len(data) - frame_size, hop_size):
        frames.append(data[start:start + frame_size])
    return np.array(frames)

def detect_spikes(frames, threshold_factor=2.5):
    energies = np.sum(frames ** 2, axis=1)
    mean_energy = np.mean(energies)
    spikes = np.where(energies > threshold_factor * mean_energy)[0]
    return spikes

def make_decision(spikes):
    if len(spikes) > 0:
        return "Out"
    else:
        return "Not Out"

def drs_system_pipeline(audio_filename):
    # Step 1: Load audio
    sample_rate, data = load_audio(audio_filename)

    # Step 2: Frame the audio
    frames = frame_audio(data, sample_rate, frame_duration_ms=10)

    # Step 3: Detect spikes
    spikes = detect_spikes(frames, threshold_factor=2.5)

    # Step 4: Make decision
    decision = make_decision(spikes)

    return decision
