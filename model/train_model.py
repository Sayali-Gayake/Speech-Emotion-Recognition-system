# import os
# import numpy as np
# import librosa
# from sklearn.model_selection import train_test_split
# from sklearn.preprocessing import LabelEncoder
# from tensorflow.keras.utils import to_categorical
# from tensorflow.keras.models import Sequential
# from tensorflow.keras.layers import Conv1D, MaxPooling1D, Dropout
# from tensorflow.keras.layers import Bidirectional, LSTM, Dense

# # -------------------------
# # PATH
# # -------------------------
# DATASET_PATH = "../dataset/RAVDESS"

# # -------------------------
# # FEATURE EXTRACTION
# # -------------------------
# def extract_features(file_path):
#     audio, sr = librosa.load(file_path, duration=3, offset=0.5)

#     mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=40)
#     mfcc = np.mean(mfcc.T, axis=0)

#     mel = librosa.feature.melspectrogram(y=audio, sr=sr)
#     mel = np.mean(mel.T, axis=0)

#     return np.hstack((mfcc, mel))

# # -------------------------
# # LOAD DATASET
# # -------------------------
# features = []
# labels = []

# emotion_map = {
#     "01": "neutral",
#     "02": "calm",
#     "03": "happy",
#     "04": "sad",
#     "05": "angry",
#     "06": "fearful",
#     "07": "disgust",
#     "08": "surprised"
# }

# for root, _, files in os.walk(DATASET_PATH):
#     for file in files:
#         if file.endswith(".wav"):
#             emotion_code = file.split("-")[2]
#             emotion = emotion_map[emotion_code]

#             file_path = os.path.join(root, file)
#             feature = extract_features(file_path)

#             features.append(feature)
#             labels.append(emotion)

# X = np.array(features)
# y = np.array(labels)

# # -------------------------
# # ENCODE LABELS
# # -------------------------
# encoder = LabelEncoder()
# y_encoded = encoder.fit_transform(y)
# y_categorical = to_categorical(y_encoded)

# # -------------------------
# # RESHAPE FOR CNN
# # -------------------------
# X = X.reshape(X.shape[0], X.shape[1], 1)

# # -------------------------
# # TRAIN TEST SPLIT
# # -------------------------
# X_train, X_test, y_train, y_test = train_test_split(
#     X, y_categorical, test_size=0.2, random_state=42
# )

# # -------------------------
# # CNN + BiLSTM MODEL
# # -------------------------
# model = Sequential()

# model.add(Conv1D(64, kernel_size=5, activation='relu', input_shape=(X.shape[1], 1)))
# model.add(MaxPooling1D(pool_size=2))
# model.add(Dropout(0.3))

# model.add(Bidirectional(LSTM(64)))
# model.add(Dense(64, activation='relu'))
# model.add(Dense(8, activation='softmax'))

# model.compile(
#     optimizer='adam',
#     loss='categorical_crossentropy',
#     metrics=['accuracy']
# )

# model.summary()

# # -------------------------
# # TRAIN MODEL
# # -------------------------
# history = model.fit(
#     X_train, y_train,
#     validation_data=(X_test, y_test),
#     epochs=50,
#     batch_size=32
# )

# # -------------------------
# # SAVE MODEL
# # -------------------------
# model.save("ser_cnn_bilstm.h5")
# print("✅ Model saved as ser_cnn_bilstm.h5")
import os
import numpy as np
import librosa
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import classification_report

from tensorflow.keras.utils import to_categorical
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv1D, MaxPooling1D, Dropout
from tensorflow.keras.layers import Bidirectional, LSTM, Dense
from tensorflow.keras.callbacks import EarlyStopping

# ---------------------------------------------
# DATASET PATH (LOCAL)
# ---------------------------------------------
DATASET_PATH = "dataset/RAVDESS"

# ---------------------------------------------
# EMOTION MAP
# ---------------------------------------------
emotion_map = {
    "01": "Neutral",
    "02": "Calm",
    "03": "Happy",
    "04": "Sad",
    "05": "Angry",
    "06": "Fearful",
    "07": "Disgust",
    "08": "Surprised"
}

# ---------------------------------------------
# AUGMENTATION
# ---------------------------------------------
def add_noise(data):
    noise = 0.005 * np.random.randn(len(data))
    return data + noise

def stretch(data):
    return librosa.effects.time_stretch(data, rate=0.8)

def pitch_shift(data, sr):
    return librosa.effects.pitch_shift(data, sr=sr, n_steps=2)

# ---------------------------------------------
# FEATURE EXTRACTION
# ---------------------------------------------
def extract_features(data, sr):
    mfcc = np.mean(librosa.feature.mfcc(y=data, sr=sr, n_mfcc=40).T, axis=0)
    chroma = np.mean(librosa.feature.chroma_stft(y=data, sr=sr).T, axis=0)
    mel = np.mean(librosa.feature.melspectrogram(y=data, sr=sr).T, axis=0)
    return np.hstack((mfcc, chroma, mel))

# ---------------------------------------------
# LOAD DATA
# ---------------------------------------------
features = []
labels = []

print("Loading dataset...")

for root, _, files in os.walk(DATASET_PATH):
    for file in files:
        if file.endswith(".wav"):
            emotion_code = file.split("-")[2]
            emotion = emotion_map[emotion_code]

            file_path = os.path.join(root, file)
            data, sr = librosa.load(file_path, duration=3, offset=0.5)

            # Original
            features.append(extract_features(data, sr))
            labels.append(emotion)

            # Augmentations
            features.append(extract_features(add_noise(data), sr))
            labels.append(emotion)

            features.append(extract_features(stretch(data), sr))
            labels.append(emotion)

            features.append(extract_features(pitch_shift(data, sr), sr))
            labels.append(emotion)

X = np.array(features)
y = np.array(labels)

print("Dataset Loaded:", X.shape)

# ---------------------------------------------
# ENCODE LABELS
# ---------------------------------------------
encoder = LabelEncoder()
y_encoded = encoder.fit_transform(y)
y_categorical = to_categorical(y_encoded)

# ---------------------------------------------
# SCALE FEATURES
# ---------------------------------------------
scaler = StandardScaler()
X = scaler.fit_transform(X)

# SAVE SCALER
os.makedirs("model", exist_ok=True)
joblib.dump(scaler, "model/scaler.pkl")

# ---------------------------------------------
# RESHAPE
# ---------------------------------------------
X = X.reshape(X.shape[0], X.shape[1], 1)

# ---------------------------------------------
# TRAIN TEST SPLIT
# ---------------------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y_categorical,
    test_size=0.2,
    random_state=42,
    stratify=y_categorical
)

# ---------------------------------------------
# MODEL
# ---------------------------------------------
model = Sequential()

model.add(Conv1D(128, 5, activation='relu', input_shape=(X.shape[1], 1)))
model.add(MaxPooling1D(2))
model.add(Dropout(0.3))

model.add(Conv1D(64, 3, activation='relu'))
model.add(MaxPooling1D(2))
model.add(Dropout(0.3))

model.add(Bidirectional(LSTM(128)))
model.add(Dropout(0.3))

model.add(Dense(64, activation='relu'))
model.add(Dense(8, activation='softmax'))

model.compile(
    optimizer='adam',
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

model.summary()

# ---------------------------------------------
# EARLY STOPPING
# ---------------------------------------------
early_stop = EarlyStopping(
    monitor='val_loss',
    patience=5,
    restore_best_weights=True
)

# ---------------------------------------------
# TRAIN
# ---------------------------------------------
history = model.fit(
    X_train, y_train,
    validation_data=(X_test, y_test),
    epochs=50,
    batch_size=32,
    callbacks=[early_stop]
)

# ---------------------------------------------
# EVALUATION
# ---------------------------------------------
print("\nClassification Report:")
y_pred = model.predict(X_test)
print(classification_report(
    np.argmax(y_test, axis=1),
    np.argmax(y_pred, axis=1),
    target_names=encoder.classes_
))

# ---------------------------------------------
# SAVE MODEL & LABELS
# ---------------------------------------------
model.save("model/ser_cnn_bilstm.h5")
np.save("model/label_classes.npy", encoder.classes_)

print("✅ Model, Labels & Scaler saved successfully!")