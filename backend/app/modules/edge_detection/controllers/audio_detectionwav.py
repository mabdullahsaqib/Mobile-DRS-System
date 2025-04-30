import base64
import io
import numpy as np
import noisereduce as nr
from pydub import AudioSegment
from pydantic import BaseModel

def decodebase64_convert_to_wav(audio: AudioData, output_path: str):
    
    audio_bytes = base64.b64decode(audio.data)
    audio_stream = io.BytesIO(audio_bytes)  #decoding the base64 string
   
   
    audio = AudioSegment.from_file(audio_stream)
    wav_stream = io.BytesIO()
    audio.export(wav_stream, format="wav")
    wav_stream.seek(0)  #converting to .wav format

    y, sr = sf.read(wav_buffer)
    return y, sr
def denoise_audio(y: np.ndarray, sr: int, output_path: str) -> tuple:   #will return the denoise audio and sample rate
    y_denoised = nr.reduce_noise(y=y, sr=sr)
    sf.write(output_path, y_denoised, sr)
    return y_denoised, sr  
