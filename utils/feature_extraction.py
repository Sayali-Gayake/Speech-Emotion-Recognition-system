import librosa
import numpy as np

def extract_features(file_path):
    audio, sr = librosa.load(file_path, duration=3, offset=0.5)

    mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=40)
    mfcc = np.mean(mfcc.T, axis=0)

    mel = librosa.feature.melspectrogram(y=audio, sr=sr)
    mel = np.mean(mel.T, axis=0)

    return np.hstack((mfcc, mel))
