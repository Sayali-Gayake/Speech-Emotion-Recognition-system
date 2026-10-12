from tensorflow.keras.models import load_model

try:
    model = load_model("ser_cnn_bilstm.h5")
    print("✅ Model Loaded Successfully\n")
    model.summary()
except Exception as e:
    print("❌ Error loading model:", e)