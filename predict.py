import librosa
import numpy as np
import os
import joblib
from tensorflow.keras.models import load_model
from pydub import AudioSegment

# ---------------- PATH SETUP ---------------- #

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MODEL_PATH = os.path.join(BASE_DIR, "model", "ser_cnn_bilstm.h5")
LABEL_PATH = os.path.join(BASE_DIR, "model", "label_classes.npy")
SCALER_PATH = os.path.join(BASE_DIR, "model", "scaler.pkl")

# ---------------- LOAD MODEL ---------------- #

model = load_model(MODEL_PATH, compile=False)
labels = np.load(LABEL_PATH)
scaler = joblib.load(SCALER_PATH)

def ensure_wav(file_path):
    if file_path.endswith(".webm"):
        wav_path = file_path.replace(".webm", ".wav")
        audio = AudioSegment.from_file(file_path, format="webm")
        audio.export(wav_path, format="wav")
        print(f"[DEBUG] Converted WebM to WAV: {wav_path}")
        return wav_path
    return file_path
# ---------------- FEATURE EXTRACTION ---------------- #

def extract_features(file_path):
    file_path=ensure_wav(file_path)
    audio, sr = librosa.load(file_path, duration=3, offset=0.5)
    print(f"[DEBUG] Loaded audio file: {file_path}, Sample rate: {sr}, Length: {len(audio)} samples")
    mfcc = np.mean(librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=40).T, axis=0)
    chroma = np.mean(librosa.feature.chroma_stft(y=audio, sr=sr).T, axis=0)
    mel = np.mean(librosa.feature.melspectrogram(y=audio, sr=sr).T, axis=0)

    features = np.hstack((mfcc, chroma, mel))

    print("Feature length:", len(features))  # should be ~176

    features = scaler.transform([features])

    features = features.reshape(features.shape[0], features.shape[1], 1)

    print("Final shape:", features.shape)  # should be (1, 176, 1)

    return features

# ---------------- DEPRESSION SCORE ---------------- #

def calculate_depression_score(prob_dict):
    score = (
        prob_dict.get("neutral", 0) * 0.1 +
        prob_dict.get("calm", 0) * -0.2 +
        prob_dict.get("happy", 0) * -0.3 +
        prob_dict.get("sad", 0) * 0.25 +
        prob_dict.get("angry", 0) * 0.2 +
        prob_dict.get("fearful", 0) * 0.15 +
        prob_dict.get("disgust", 0) * 0.25 +
        prob_dict.get("surprised", 0) * 0.05
    )

    score = max(0, min(score * 100, 100))
    return round(score, 2)

# ---------------- MAIN FUNCTION ---------------- #

def predict_emotion(file_path):
    features = extract_features(file_path)

    prediction = model.predict(features, verbose=0)[0]

    print("Prediction:", prediction)

    prob_dict = {
        labels[i].lower(): float(prediction[i])
        for i in range(len(labels))
    }

    predicted_emotion = max(prob_dict, key=prob_dict.get)
    confidence = round(prob_dict[predicted_emotion] * 100, 2)

    depression_score = calculate_depression_score(prob_dict)

    if depression_score > 60:
        risk = "High"
    elif depression_score > 35:
        risk = "Medium"
    else:
        risk = "Low"

    instability = round(100 - confidence, 2)

    return predicted_emotion, confidence, risk, prob_dict, depression_score, instability