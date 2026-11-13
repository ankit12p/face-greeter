import sqlite3
import pickle

DB_PATH = "faces.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            name TEXT PRIMARY KEY,
            encoding BLOB NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def save_face(name, encoding):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    data = pickle.dumps(encoding)
    c.execute(
        "INSERT OR REPLACE INTO users (name, encoding) VALUES (?, ?)",
        (name, data),
    )
    conn.commit()
    conn.close()
    print(f"[DB] Saved face for '{name}'")


def load_faces():
    init_db()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT name, encoding FROM users")
    rows = c.fetchall()
    conn.close()

    names, encodings = [], []
    for name, blob in rows:
        names.append(name)
        encodings.append(pickle.loads(blob))
    return names, encodings


def list_users():
    init_db()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT name FROM users")
    rows = c.fetchall()
    conn.close()
    return [r[0] for r in rows]


if __name__ == "__main__":
    init_db()
    print("Database initialized.")
    print("Current users:", list_users())