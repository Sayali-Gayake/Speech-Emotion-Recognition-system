import sqlite3

conn = sqlite3.connect("dashboard.db")
c = conn.cursor()
c.execute("SELECT id, user_name, emotion, confidence, depression_score, risk, date FROM results")
rows = c.fetchall()
for row in rows:
    print(row)
conn.close()
# import sqlite3

# conn = sqlite3.connect("history.db")
# c = conn.cursor()
# c.execute("UPDATE users SET role = 'admin' WHERE name = 'Prajakta Dhage'")
# conn.commit()
# conn.close()