import base64
import io
import numpy as np
import noisereduce as nr
from pydub import AudioSegment
from pydantic import BaseModel


class AudioData(BaseModel):
    data: str  


def decodebase64_convert_to_wav(audio: AudioData, output_path: str) -> str:

    audio_bytes = base64.b64decode(audio.data)
    audio_stream = io.BytesIO(audio_bytes)

    # Convert to WAV using pydub
    audio_segment = AudioSegment.from_file(audio_stream)
    audio_segment = audio_segment.set_channels(1)  # Force mono to simplify
    audio_segment.export(output_path, format="wav")

    return output_path  # Return path to be used in pipeline

def denoise_audio(input_path: str, output_path: str) -> None:
#reads wav file denoises it and saves to another wav file
    y, sr = sf.read(input_path)
    y_denoised = nr.reduce_noise(y=y, sr=sr)
    sf.write(output_path, y_denoised, sr)