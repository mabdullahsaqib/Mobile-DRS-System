import numpy as np
import scipy.io.wavfile as wav
from modules.edge_detection.controllers.audio_detectionwav import decodebase64_pcm_to_wav,denoise_audio

def load_audio(filename):
    sample_rate, data = wav.read(filename)
    if len(data.shape) == 2:
        data = data[:, 0]
    return sample_rate, data

def frame_audio(data, sample_rate, frame_duration_ms=10):
    frame_size = int(sample_rate * (frame_duration_ms / 1000))
    hop_size = frame_size
    frames = []
    for start in range(0, len(data) - frame_size, hop_size):
        frames.append(data[start:start + frame_size])

    frames = np.array(frames)

    # Ensure it's 2D
    if frames.ndim == 1:
        frames = frames[:, np.newaxis]

    return frames

def detect_spikes(frames, threshold_factor=2.5):
    # Ensure frames is a 2D array
    if frames.ndim == 1:
        frames = frames[:, np.newaxis]
    energies = np.sum(frames ** 2, axis=1)
    mean_energy = np.mean(energies)
    spikes = np.where(energies > threshold_factor * mean_energy)[0]
    return spikes


def make_decision(spikes):
    if len(spikes) > 0:
        return "Out"
    else:
        return "Not Out"

def drs_system_pipeline(audio_data_base64) -> str:

    audio_base64 = audio_data_base64
    # Step 1: Decode and convert to WAV
    raw_wav_path = "../../../assets/raw_audio.wav"
    cleaned_wav_path = "../../../assets/denoised_audio.wav"
    decodebase64_pcm_to_wav(audio_base64, raw_wav_path)

    # Step 2: Denoise
    denoise_audio(raw_wav_path, cleaned_wav_path)

    # Step 3: Load audio (from cleaned file)
    sample_rate, data = load_audio(cleaned_wav_path)

    # Step 4: Frame the audio
    frames = frame_audio(data, sample_rate, frame_duration_ms=10)

    # Step 5: Detect spikes
    spikes = detect_spikes(frames, threshold_factor=2.5)

    # Step 6: Make decision
    decision = make_decision(spikes)

    return decision
