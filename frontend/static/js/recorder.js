let mediaRecorder;
let audioChunks = [];
const recordBtn = document.getElementById("recordBtn");
const stopBtn = document.getElementById("stopBtn");
const analyzeBtn = document.getElementById("analyzeBtn");
const canvas = document.getElementById("waveform");
const ctx = canvas.getContext("2d");
const recordingBox = document.getElementById("recordingBox");
const recordingStatus = document.getElementById("recordingStatus");

recordBtn.addEventListener("click", async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

    mediaRecorder = new MediaRecorder(stream);
    audioChunks = [];

    mediaRecorder.ondataavailable = event => {
        audioChunks.push(event.data);
    };

    mediaRecorder.start();

    // 🔵 UI Changes When Recording Starts
    recordBtn.disabled = true;
    stopBtn.disabled = false;

    recordingBox.classList.add("active");
    recordingStatus.innerText = "🎙️ Recording in Progress...";
});

stopBtn.addEventListener("click", () => {
    mediaRecorder.stop();

    mediaRecorder.onstop = async () => {

        // Create WAV blob
        const blob = new Blob(audioChunks, { type: "audio/wav" });

        const formData = new FormData();
        formData.append("audio", blob, "recording.wav");

        // 🔵 UI Changes When Recording Stops
        recordingBox.classList.remove("active");
        recordingStatus.innerText = "⏳ Analyzing Recording...";

        await fetch("/upload_live_audio", {
            method: "POST",
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            // Redirect to result page with prediction values
            window.location.href = `/result?emotion=${data.emotion}&confidence=${data.confidence}&risk=${data.risk}&depression_score=${data.score}&source_type=Live+Audio`;
        })
        .catch(err => {
            alert("Error uploading audio: " + err);
        });

    };

    recordBtn.disabled = false;
    stopBtn.disabled = true;
});