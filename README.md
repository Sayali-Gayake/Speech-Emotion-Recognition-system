
# Speech Emotion Recognition for Early Detection of Depression and Mental Health Issues

An AI/ML-based Speech Emotion Recognition (SER) system that analyzes speech signals, classifies emotional states, and explores their potential use in early depression-risk screening using deep learning.

## Abstract

Depression is a common mental health condition that can be difficult to identify at an early stage. This project develops a Speech Emotion Recognition system that analyzes speech signals to identify emotional states that may be associated with psychological well-being.

The system extracts audio features such as Mel Frequency Cepstral Coefficients (MFCC), Chroma, and Mel Spectrograms and uses a CNN-BiLSTM deep learning model for emotion classification. A Flask-based web application provides audio analysis, prediction results, history tracking, dashboard visualization, and report generation.

The project explores how speech emotion analysis may support preliminary mental health risk research. It is intended for educational and research purposes and is not a clinical diagnostic system.

## Introduction

Human speech contains acoustic information, including pitch, tone, rhythm, and spectral characteristics, that may convey emotional states such as happiness, sadness, anger, fear, and neutrality.

Speech Emotion Recognition uses audio processing and machine learning to classify emotions from speech recordings. This project combines audio feature extraction with a CNN-BiLSTM architecture to identify emotional patterns and explore their potential relevance to early depression-risk screening.

The system also provides a web interface to analyze audio and review prediction history.

## Objectives

- Develop a machine learning-based Speech Emotion Recognition system.
- Extract meaningful speech features using audio signal processing techniques.
- Train and evaluate deep learning models for emotion classification.
- Explore emotion-based indicators for preliminary depression-risk research.
- Develop a web application for audio analysis and prediction visualization.
- Maintain prediction history and generate reports.

## Key Features

- Audio input and preprocessing.
- Speech feature extraction using MFCC, Chroma, and Mel Spectrograms.
- Emotion classification using a CNN-BiLSTM model.
- Flask-based web application.
- Audio upload and live audio analysis, where supported.
- Prediction confidence and emotion probability visualization.
- Dashboard with prediction history.
- Risk-level classification using configured application rules.
- Historical result review and PDF report generation.
- User authentication and profile features, where enabled.

## Tools and Technologies

| Category | Technologies |
|---|---|
| Programming Language | Python |
| Deep Learning | TensorFlow, Keras |
| Audio Processing | Librosa, SciPy, Pydub |
| Feature Extraction | MFCC, Chroma, Mel Spectrogram |
| Machine Learning | Scikit-learn |
| Data Processing | NumPy, Pandas |
| Data Visualization | Matplotlib, Seaborn |
| Web Framework | Flask, Flask-SocketIO |
| Database | SQLite |
| Frontend | HTML, CSS, JavaScript |
| Cloud Deployment | AWS, if applicable to the deployed version |

## System Workflow

1. **Audio Input:** The user provides a speech recording or supported live audio input.
2. **Preprocessing:** The audio is converted into the required format and prepared for analysis.
3. **Feature Extraction:** Relevant acoustic features are extracted using audio processing techniques.
4. **Emotion Classification:** The trained CNN-BiLSTM model processes the extracted features.
5. **Prediction Output:** The application displays the predicted emotion and available confidence or probability scores.
6. **Risk Analysis:** Configured rules generate an experimental risk indicator from selected emotion-related information.
7. **History Management:** Prediction results are stored in the application's SQLite database.
8. **Visualization and Reporting:** Users can review available history, dashboard charts, and generated reports.

## Dataset

The project uses the **RAVDESS (Ryerson Audio-Visual Database of Emotional Speech and Song)** dataset for speech emotion recognition.

Dataset link: https://zenodo.org/records/1188976

The dataset contains acted emotional speech and song recordings. It is used for emotion classification research and should not be treated as direct clinical evidence of depression.

## Model Architecture

The project uses a **Convolutional Neural Network with Bidirectional Long Short-Term Memory (CNN-BiLSTM)** architecture.

- **CNN:** Learns local patterns from the extracted audio features.
- **BiLSTM:** Learns sequential patterns in the feature representation.
- **Classification layer:** Produces predictions across the emotion classes supported by the trained model.

The model's performance depends on the dataset, preprocessing pipeline, training configuration, and evaluation methodology.

## Model Evaluation

The following results are the project's reported evaluation metrics:

| Metric | Reported Result |
|---|---:|
| Model | CNN-BiLSTM |
| Accuracy | 91.8% |
| F1-score | 90.1% |

These figures describe the reported emotion-classification evaluation. They do not establish clinical accuracy for detecting depression.

For reproducibility, document the test-set split, emotion classes, averaging method for the F1-score, and evaluation procedure used to obtain these results.

## Installation and Setup

### Prerequisites

- Python 3.8+ or a compatible version supported by the project's dependencies.
- Git.
- VS Code or another Python editor.
- Required model files and dataset, if needed by the selected workflow.



### 1. Create a Virtual Environment

```bash
python -m venv venv
```

**Windows:**

```bash
venv\Scripts\activate
```

**Linux/macOS:**

```bash
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

If `requirements.txt` has not been created yet, install the project's verified dependencies before generating the file.

### 3. Configure the Application

- Ensure that the trained model is available at the path expected by the application.
- Configure dataset and database paths as required.
- Set environment variables for any required configuration.
- Never commit passwords, AWS access keys, API tokens, or secret configuration files.

### 4. Run the Application

If `app.py` is the application entry point, run:

```bash
python app.py
```

Open the local URL printed in the terminal. The exact command and URL may differ depending on your application configuration.

## Project Structure

The following is an illustrative structure. Adjust it to match the actual files in the repository.

```text
speech-emotion-recognition-cnn-bilstm/
├── app.py
├── backend/
│   └── predict.py
├── templates/
├── static/
├── models/
├── requirements.txt
├── .gitignore
└── README.md
```

## Applications

- Speech emotion classification research.
- Educational demonstrations of audio-based deep learning.
- Exploration of acoustic emotion patterns.
- Experimental mental health risk research.

## Limitations

- Speech emotion predictions may be affected by noise, accents, language, culture, and recording quality.
- Acted emotional speech may not fully represent emotions in real-world conversations.
- Emotion classification alone cannot diagnose depression.
- The risk indicator is based on configured application rules and should not be interpreted as a validated clinical score.
- Results should be interpreted cautiously and should not replace professional mental health assessment.

## Future Improvements

- Evaluate the model across different speakers and recording conditions.
- Improve robustness to background noise.
- Perform more extensive testing and error analysis.
- Explore additional validated datasets and suitable evaluation protocols.
- Improve privacy and security practices for audio storage.
- Enhance deployment reliability, monitoring, and scalability.

## Disclaimer

This project is intended for educational and research purposes only. It is not intended to diagnose, treat, or prevent depression or any other mental health condition. Speech emotion predictions are uncertain and should not be used as the sole basis for medical or mental health decisions.

## Author

**Sayali Ramprasad Gayake**

BE Computer Engineering Graduate

**Areas of Interest:** Artificial Intelligence, Machine Learning, Deep Learning, Python, and AWS.

---

If you find this project useful, feel free to explore the repository and share your feedback.
