import sqlite3

conn = sqlite3.connect("history.db")
c = conn.cursor()

# Add role column if it doesn't exist
try:
    c.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'user'")
    conn.commit()
    print("Role column added successfully.")
except Exception as e:
    print("Error:", e)

# Set Sayali Gayake as admin
c.execute("UPDATE users SET role = 'admin' WHERE name = 'Sayali Gayake'")
conn.commit()

conn.close()
print("Sayali Gayake set as admin.")