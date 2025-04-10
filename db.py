import sqlite3

# database initialization
def init_db():
    conn = sqlite3.connect("weather.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS weather (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            forecast_id TEXT,
            city TEXT,
            date TEXT,
            temperature REAL,
            description TEXT
        )
    """)
    conn.commit()
    conn.close()