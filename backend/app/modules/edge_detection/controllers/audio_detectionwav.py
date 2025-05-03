import base64
import io
from pydub import AudioSegment
from pydantic import BaseModel
import soundfile as sf
import numpy as np
import noisereduce as nr
import scipy.io.wavfile as wav

def decodebase64_convert_to_wav(audio, output_path: str) -> str:
    """Decodes a base64 audio string and saves it as a WAV file."""
    audio_bytes = base64.b64decode(audio)
    audio_stream = io.BytesIO(audio_bytes)

    # Convert to WAV using pydub
    audio_segment = AudioSegment.from_file(audio_stream)
    audio_segment = audio_segment.set_channels(1)  # Force mono to simplify
    audio_segment.export(output_path, format="wav")

    return output_path  # Return path to be used in pipeline

def denoise_audio(input_path: str, output_path: str) -> None:
    """Reads WAV file, denoises it, and saves to another WAV file."""
    y, sr = sf.read(input_path)
    y_denoised = nr.reduce_noise(y=y, sr=sr)
    sf.write(output_path, y_denoised, sr)