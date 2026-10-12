from flask import Flask, render_template, request, redirect, url_for, session, send_file
from flask_socketio import SocketIO, emit
from flask import jsonify
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os
from backend.predict import predict_emotion
import json
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from collections import defaultdict
from pydub import AudioSegment
import uuid
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", os.urandom(24))
socketio = SocketIO(app, cors_allowed_origins="*")

EMAIL_ADDRESS = os.environ.get("EMAIL_ADDRESS", "your_email@gmail.com")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD", "your_app_password")

# ------------------ Database Setup ------------------
def init_db():
    conn = sqlite3.connect("history.db")
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        email TEXT,
        age INTEGER,
        password TEXT,
        role TEXT DEFAULT 'user'
    )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT,
            emotion TEXT,
            confidence REAL,
            risk TEXT,
            depression_score INTEGER,
            probabilities TEXT,
            date TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT,
            question TEXT,
            answer TEXT,
            audio_file TEXT,
            date TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ------------------ Root Route ------------------
@app.route("/", methods=["GET", "POST"])
def home():
    if "user" not in session:
        return redirect(url_for("login"))
    return redirect(url_for("index"))


# ------------------ Index (Analysis) ------------------
# @app.route("/index", methods=["GET", "POST"])
# def index():
#     if "user" not in session:
#         return redirect(url_for("login"))

#     if request.method == "POST":
#         audio_file = request.files.get("audio")
#         if audio_file:
#             uploads_dir = os.path.join(os.getcwd(), "uploads")
#             os.makedirs(uploads_dir, exist_ok=True)
#             file_path = os.path.join(uploads_dir, audio_file.filename)
#             audio_file.save(file_path)
#             emotion, confidence, risk, prob_dict, score, instability = predict_emotion(file_path)
#             labels = list(prob_dict.keys())
#             probabilities = list(prob_dict.values())
#             risk_value = score

#             conn = sqlite3.connect("history.db")
#             c = conn.cursor()

#             c.execute("""
#             INSERT INTO history (user_name, emotion, confidence, risk, depression_score, probabilities, date)
#             VALUES (?, ?, ?, ?, ?, ?, DATE('now'))
#             """, (
#                 session.get("user"),
#                 emotion,
#                 confidence,
#                 risk,
#                 score,
#                 json.dumps(prob_dict)
#             ))
#             conn.commit()
#             conn.close()
#             return render_template(
#                 "result.html",
#                 emotion=emotion,
#                 confidence=confidence,
#                 risk=risk,
#                 depression_score=score,
#                 labels=list(prob_dict.keys()),
#                 probabilities=list(prob_dict.values()),
#                 instability=instability,
#                 user_name=session.get("user")
#             )
#     return render_template("index.html")
# ------------------ Index (Recorded Audio Analysis) ------------------
@app.route("/index", methods=["GET", "POST"])
def index():
    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        if "audio" not in request.files:
            return jsonify({"error": "No audio received"}), 400

        audio_file = request.files["audio"]
        uploads_dir = os.path.join(os.getcwd(), "uploads")
        os.makedirs(uploads_dir, exist_ok=True)
        file_path = os.path.join(uploads_dir, audio_file.filename)
        audio_file.save(file_path)

        # Run prediction
        emotion, confidence, risk, prob_dict, score, instability = predict_emotion(file_path)

        # Save to DB
        conn = sqlite3.connect("history.db")
        c = conn.cursor()
        c.execute("""
            INSERT INTO history (user_name, emotion, confidence, risk, depression_score, probabilities, date)
            VALUES (?, ?, ?, ?, ?, ?, DATE('now'))
        """, (session.get("user"), emotion, confidence, risk, score, json.dumps(prob_dict)))
        conn.commit()
        conn.close()

        # Store probabilities for result page
        session["probabilities"] = prob_dict

        # ✅ Return JSON instead of rendering template
        return jsonify({
            "emotion": emotion,
            "confidence": confidence,
            "risk": risk,
            "score": score,
            "probabilities": prob_dict,
            "file_size": os.path.getsize(file_path),
            "duration": len(AudioSegment.from_file(file_path)) / 1000,  # ms → seconds
            "source_type": "Recorded Audio"
        })

    # For GET requests, just render the upload page
    return render_template("index.html")

# ---------------------Live Audio--------------------------
@app.route("/upload_live_audio", methods=["POST"])
def upload_live_audio():
    if "user" not in session:
        return jsonify({"error": "Not logged in"}), 401

    if "audio" not in request.files:
        return jsonify({"error": "No audio received"}), 400

    audio_file = request.files["audio"]
    uploads_dir = os.path.join(os.getcwd(), "uploads")
    os.makedirs(uploads_dir, exist_ok=True)
    filename = f"{uuid.uuid4()}_{audio_file.filename}"
    file_path = os.path.join(uploads_dir, filename)
    audio_file.save(file_path)
    if file_path.endswith(".webm"):
        wav_path = file_path.replace(".webm", ".wav")
        audio = AudioSegment.from_file(file_path, format="webm")
        audio.export(wav_path, format="wav")
        print(f"[DEBUG] Converted WebM to WAV: {wav_path}")
        file_path = wav_path
    emotion, confidence, risk, prob_dict, score, instability = predict_emotion(file_path)
    session["probabilities"] = prob_dict
    # Log results in console
    # print("=== Prediction Result ===")
    # print(f"Emotion: {emotion}")
    # print(f"Confidence: {confidence:.2f}")
    # print(f"Risk Level: {risk}")
    # print(f"Depression Score: {score}")
    # print(f"Probabilities: {prob_dict}")
    # print(f"Instability: {instability}")
    # print("=========================")

    # Save to DB
    conn = sqlite3.connect("history.db")
    c = conn.cursor()
    c.execute("""
        INSERT INTO history (user_name, emotion, confidence, risk, depression_score, probabilities, date)
        VALUES (?, ?, ?, ?, ?, ?, DATE('now'))
    """, (session.get("user"), emotion, confidence, risk, score, json.dumps(prob_dict)))
    conn.commit()
    conn.close()

    # Return JSON response
    return jsonify({
    "emotion": emotion,
    "confidence": confidence,
    "risk": risk,
    "score": score,
    "probabilities": prob_dict,
    "file_size": os.path.getsize(file_path),
    "duration": len(AudioSegment.from_file(file_path)) / 1000 , # ms → seconds
    "source_type":"Live Audio"
    })

# ------------------ WebSocket for Live Audio ------------------
@socketio.on("audio_chunk")
def handle_audio_chunk(data):
    if "user" not in session:
        emit("error", {"message": "Not logged in"})
        return

    uploads_dir = os.path.join(os.getcwd(), "uploads")
    os.makedirs(uploads_dir, exist_ok=True)
    file_path = os.path.join(uploads_dir, data["filename"])

    with open(file_path, "wb") as f:
        f.write(data["content"])

    emotion, confidence, risk, prob_dict, score, instability = predict_emotion(file_path)

    conn = sqlite3.connect("history.db")
    c = conn.cursor()
    c.execute("""
        INSERT INTO history (user_name, emotion, confidence, risk, depression_score, probabilities, date)
        VALUES (?, ?, ?, ?, ?, ?, DATE('now'))
    """, (session.get("user"), emotion, confidence, risk, score, json.dumps(prob_dict)))
    conn.commit()
    conn.close()

    emit("prediction", {
        "emotion": emotion,
        "confidence": confidence,
        "risk": risk,
        "score": score,
        "probabilities": prob_dict
    })

# ---------------------------------------------
@app.route("/result")
def result():
    emotion = request.args.get("emotion")
    confidence = request.args.get("confidence")
    risk = request.args.get("risk")
    depression_score = request.args.get("depression_score")
    file_size = request.args.get("file_size")
    duration = request.args.get("duration")
    source_type = request.args.get("source_type")

    # Get probabilities if passed (JSON encoded in query or session)
    probabilities = session.get("probabilities", {
        "Angry": 0,
        "Neutral": 0,
        "Surprised": 0,
        "Sad": 0,
        "Happy": 0,
        "Fear": 0,
        "Disgust": 0,
        "Calm":0
    })
    labels = list(probabilities.keys())
    values = list(probabilities.values())
    return render_template(
        "result.html",
        emotion=emotion,
        confidence=confidence,
        risk=risk,
        depression_score=depression_score,
        source_type=source_type,
        user_name=session.get("user"),
        labels=labels,
        probabilities=values
    )

# ------------------ Registration ------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        age = request.form["age"]
        password = request.form["password"]

        hashed_password = generate_password_hash(password)

        try:
            conn = sqlite3.connect("history.db")
            c = conn.cursor()
            c.execute("INSERT INTO users (name, password, role, email, age) VALUES (?, ?, ?, ?, ?)",
                      (name, hashed_password, "user", email, age))
            conn.commit()
            conn.close()
        except sqlite3.IntegrityError:
            return render_template("register.html", error="Username or email already exists!")

        return redirect(url_for("login"))

    return render_template("register.html")

# ------------------ Login ------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form["name"]
        password = request.form["password"]

        conn = sqlite3.connect("history.db")
        c = conn.cursor()
        c.execute("SELECT password, role FROM users WHERE name = ?", (name,))
        result = c.fetchone()
        conn.close()

        if result and check_password_hash(result[0], password):
            session["user"] = name
            session["role"] = result[1]

            if result[1] == "admin":
                return redirect(url_for("admin", selected_user="all"))
            else:
                return redirect(url_for("dashboard", user_name=name))
        else:
            return render_template("login.html", error="Invalid credentials!")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return render_template("logout.html", message="You have been logged out successfully.")

# ------------------ Dashboard ------------------
from collections import defaultdict

@app.route("/dashboard/")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))

    user_name = session.get("user")
    role = session.get("role")

    conn = sqlite3.connect("history.db")
    c = conn.cursor()

    if role == "admin":
        c.execute("SELECT date, probabilities FROM history")
    else:
        c.execute("SELECT date, probabilities FROM history WHERE user_name=?", (user_name,))
    rows = c.fetchall()
    conn.close()

    # Aggregate emotion counts
    emotion_totals = {}
    risk_by_date = defaultdict(list)   # ✅ new

    for row in rows:
        prob_dict = json.loads(row[1]) if row[1] else {}

        neg_total = sum(prob_dict.get(e,0) for e in ["sad","disgust","fearful","angry"])
        risk_by_date[row[0]].append(round(neg_total*100,2))   # ✅ group by date

        # still update emotion_totals
        for emotion, prob in prob_dict.items():
            emotion_totals[emotion] = emotion_totals.get(emotion, 0) + prob

    # Aggregate: average risk per day ✅
    daily_risk = [{"date": d, "risk": sum(vals)/len(vals)} for d, vals in risk_by_date.items()]

    # Sort by date and keep last 14 days ✅
    daily_risk.sort(key=lambda x: x["date"])
    daily_risk = daily_risk[-14:]

    # Normalize to percentages
    total = sum(emotion_totals.values())
    emotion_distribution = {e: v/total for e,v in emotion_totals.items()} if total>0 else {}

    # Risk calculation
    neg_total = sum(emotion_distribution.get(e,0) for e in ["sad","disgust","fearful","angry"])
    risk_value = round(neg_total*100,2)

    # Most frequent emotion
    most_frequent_emotion = max(emotion_distribution, key=emotion_distribution.get) if emotion_distribution else "N/A"

    # Risk level badge
    if risk_value >= 60:
        risk_level = "High"
    elif risk_value >= 30:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    # ✅ convert dict to lists for chart
    emotion_labels = list(emotion_distribution.keys())
    emotion_values = list(emotion_distribution.values())

    return render_template("dashboard.html",
                           user_name=user_name,
                           emotion_labels=emotion_labels,
                           emotion_values=emotion_values,
                           risk_value=risk_value,
                           most_frequent_emotion=most_frequent_emotion,
                           risk_level=risk_level,
                           daily_risk=daily_risk)


# ------------------ History ------------------
@app.route("/history", methods=["GET"])
def history():
    if "user" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect("history.db")
    conn.row_factory = sqlite3.Row

    c = conn.cursor()
    c.execute("SELECT * FROM history WHERE user_name = ?", (session["user"],))
    data = c.fetchall()
    conn.close()

    avg_score = sum([row[5] for row in data]) / len(data) if data else 0
    overall_risk = "High" if any(row[4] == "High" for row in data) else \
                   "Medium" if any(row[4] == "Medium" for row in data) else "Low"

    labels = ["Happy", "Sad", "Angry", "Neutral"]
    probabilities = [0.4, 0.2, 0.25, 0.15]
    risk_distribution = [10, 5, 3]

    last_emotion = data[-1] if data else "Neutral"
    last_confidence = data[-1]if data else 0
    last_risk = data[-1]if data else "Low"
    last_score = data[-1]if data else 0

    return render_template("user_history.html",
                           history=data,
                           user_name=session["user"],
                           avg_score=avg_score,
                           overall_risk=overall_risk,
                           labels=labels,
                           probabilities=probabilities,
                           risk_distribution=risk_distribution,
                           last_emotion=last_emotion,
                           last_confidence=last_confidence,
                           last_risk=last_risk,
                           last_score=last_score)
# ------------------ Download Full History ------------------
@app.route("/download_full_history/<user_name>")
def download_full_history(user_name):
    if "user" not in session or session["user"] != user_name:
        return redirect(url_for("login"))

    conn = sqlite3.connect("history.db")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT date, emotion, confidence, risk, depression_score FROM history WHERE user_name=? ORDER BY date DESC", (user_name,))
    records = c.fetchall()
    conn.close()

    if not records:
        return "No history available", 404

    # Generate PDF with table
    os.makedirs("reports", exist_ok=True)
    file_path = f"reports/{user_name}_full_history.pdf"
    doc = SimpleDocTemplate(file_path, pagesize=A4)

    styles = getSampleStyleSheet()
    elements = []

    # Title
    elements.append(Paragraph(f"Full History Report for {user_name}", styles['Title']))

    # Table data (header + rows)
    data = [["Date", "Emotion", "Confidence (%)", "Score (/100)", "Risk"]]
    for record in records:
        data.append([
            record["date"],
            record["emotion"],
            f"{record['confidence']}%",
            str(record["depression_score"]),
            record["risk"]
        ])

    # Create table
    table = Table(data, colWidths=[100, 100, 100, 100, 80])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.grey),
        ("TEXTCOLOR", (0,0), (-1,0), colors.whitesmoke),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0,0), (-1,0), 12),
        ("GRID", (0,0), (-1,-1), 1, colors.black),
    ]))

    elements.append(table)
    doc.build(elements)

    return send_file(file_path, as_attachment=True)

# ------------------ Admin History ------------------
@app.route("/admin", methods=["GET"])
def admin():
    if "user" not in session or session.get("role") != "admin":
        return redirect(url_for("login"))

    selected_user = request.args.get("selected_user", "all")
    conn = sqlite3.connect("history.db")
    c = conn.cursor()

    if selected_user == "all":
        c.execute("""
        SELECT id, user_name, emotion, confidence, risk, depression_score, date
        FROM history
        ORDER BY date DESC
        """)
        data = c.fetchall()
        c.execute("SELECT * FROM responses")
        responses = c.fetchall()
    else:
        c.execute("""
        SELECT id, user_name, emotion, confidence, risk, depression_score, date
        FROM history
        WHERE user_name = ?
        ORDER BY date DESC
        """, (selected_user,))
        data = c.fetchall()
        c.execute("SELECT * FROM responses WHERE user_name = ?", (selected_user,))
        responses = c.fetchall()


    c.execute("SELECT name FROM users")
    users = [row[0] for row in c.fetchall()]
    conn.close()

    avg_score = sum([row[5] for row in data]) / len(data) if data else 0
    overall_risk = "High" if any(row[4] == "High" for row in data) else \
                   "Medium" if any(row[4] == "Medium" for row in data) else "Low"

    return render_template("admin.html",
                           data=data,
                           responses=responses,
                           users=users,
                           user_name=selected_user,
                           avg_score=avg_score,
                           overall_risk=overall_risk)

# ------------------ Report Generation ------------------
def generate_report(user_name, emotion, confidence, risk, score):
    os.makedirs("reports", exist_ok=True)
    file_path = f"reports/{user_name}_report.pdf"
    pdf = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4

    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(50, height - 50, "Depression Risk Assessment Report")

    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, height - 100, f"User: {user_name}")
    pdf.drawString(50, height - 120, f"Detected Emotion: {emotion}")
    pdf.drawString(50, height - 140, f"Confidence: {confidence}%")
    pdf.drawString(50, height - 160, f"Depression Score: {score}/100")
    pdf.drawString(50, height - 180, f"Risk Level: {risk}")

    conn = sqlite3.connect("history.db")
    cursor = conn.cursor()
    cursor.execute("SELECT question, answer, date FROM responses WHERE user_name = ?", (user_name,))
    responses = cursor.fetchall()
    conn.close()

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, height - 220, "Responses to DAIC-WOZ Questions:")

    y = height - 240
    pdf.setFont("Helvetica", 12)
    for q, a, d in responses:
        pdf.drawString(50, y, f"Q: {q}")
        y -= 20
        pdf.drawString(70, y, f"A: {a}")
        y -= 20
        pdf.drawString(70, y, f"Date: {d}")
        y -= 30
        if y < 100:
            pdf.showPage()
            y = height - 100
            pdf.setFont("Helvetica", 12)

    pdf.save()
    return file_path


# ------------------ Report Download & Email ------------------
@app.route("/download_report/<user_name>/<emotion>/<confidence>/<risk>/<score>")
def download_report(user_name, emotion, confidence, risk, score):
    file_path = generate_report(user_name, emotion, confidence, risk, score)

    conn = sqlite3.connect("history.db")
    cursor = conn.cursor()
    cursor.execute("SELECT email FROM users WHERE name = ?", (user_name,))
    result = cursor.fetchone()
    conn.close()

    if result:
        user_email = result[0]
        msg = MIMEMultipart()
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = user_email
        msg["Subject"] = "Your Depression Risk Assessment Report"

        body = MIMEText(
            f"Hello {user_name},\n\nAttached is your depression risk assessment report "
            f"including your DAIC-WOZ responses.\n\nRegards,\nSER System"
        )
        msg.attach(body)

        with open(file_path, "rb") as f:
            attach = MIMEApplication(f.read(), _subtype="pdf")
            attach.add_header("Content-Disposition", "attachment", filename=f"{user_name}_report.pdf")
            msg.attach(attach)

        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                server.send_message(msg)
        except Exception as e:
            print("Error sending email:", e)

    return send_file(file_path, as_attachment=True)


# ------------------ Save Responses ------------------
@app.route("/save_response", methods=["POST"])
def save_response():
    user_name = session.get("user")
    data = request.get_json()
    responses = data.get("responses", [])

    conn = sqlite3.connect("history.db")
    cursor = conn.cursor()
    for r in responses:
        audio_file_path = r.get("audio_file", "uploads/default.wav")
        cursor.execute(
            "INSERT INTO responses (user_name, question, answer, audio_file, date) VALUES (?, ?, ?, ?, DATE('now'))",
            (user_name, r["question"], r["answer"], audio_file_path)
        )
    conn.commit()
    conn.close()

    return {"status": "saved"}
# ------------------ About Page ------------------
@app.route("/about")
def about():
    return render_template("about.html")


if __name__ == "__main__":
    socketio.run(app, host="127.0.0.1", port=5000, debug=True)