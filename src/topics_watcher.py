import sqlite3

DB_PATH = "topics_watcher.db"

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS posted_topics(
                url TEXT PRIMARY KEY,
                posted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

def is_posted(url: str) -> bool:
    with sqlite3.connect(DB_PATH) as conn:
        result = conn.execute(
                "SELECT 1 FROM posted_topics WHERE url = ?",
                (url,)
                ).fetchone()
    return result is not None

def mark_as_sended(url: str):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
                "INSERT OR IGNORE INTO posted_topics (url) VALUES (?)",
                (url,)
                )

