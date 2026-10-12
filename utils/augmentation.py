import librosa
import numpy as np

def pitch_shift(audio, sr):
    return librosa.effects.pitch_shift(audio, sr=sr, n_steps=2)

def time_stretch(audio):
    return librosa.effects.time_stretch(audio, rate=0.8)

def add_noise(audio):
    noise = np.random.randn(len(audio))
    return audio + 0.005 * noise
