import sqlite3

conn = sqlite3.connect("history.db")
c = conn.cursor()

# Drop old table
c.execute("DROP TABLE IF EXISTS results")

# Recreate with new schema
c.execute("""
    CREATE TABLE results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_name TEXT,
        emotion TEXT,
        confidence REAL,
        depression_score REAL,
        risk TEXT,
        instability REAL,
        date TEXT,
        labels TEXT,
        probabilities TEXT
    )
""")

conn.commit()
conn.close()

print("✅ Database reset complete. New schema created.")