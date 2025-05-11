import base64
import io
from pydub import AudioSegment
from pydantic import BaseModel
import soundfile as sf
import numpy as np
import noisereduce as nr
import scipy.io.wavfile as wav

def decodebase64_pcm_to_wav(audio_base64: str, output_path: str,
                            sample_rate: int = 16000,
                            sample_width: int = 2,
                            channels: int = 1) -> str:
    """Decodes base64-encoded raw PCM, saves as WAV, and denoises."""

    # Step 1: Decode Base64 to raw PCM bytes
    pcm_bytes = base64.b64decode(audio_base64)

    # Step 2: Convert PCM bytes to numpy array
    dtype = np.int16 if sample_width == 2 else np.int8  # 16-bit or 8-bit PCM
    audio_np = np.frombuffer(pcm_bytes, dtype=dtype)

    # If stereo, reshape accordingly
    if channels > 1:
        audio_np = audio_np.reshape((-1, channels))

    # Step 3: Save to WAV
    sf.write(output_path, audio_np, samplerate=sample_rate)

def denoise_audio(input_path: str, output_path: str) -> None:
    """Reads WAV file, denoises it, and saves to another WAV file."""
    y, sr = sf.read(input_path)
    y_denoised = nr.reduce_noise(y=y, sr=sr)
    sf.write(output_path, y_denoised, sr)