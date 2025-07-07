import sqlite3

def create_db():
    conn = sqlite3.connect('metrics.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            cpu REAL,
            memory REAL,
            status TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Run this file once to create the database
if __name__ == '__main__':
    create_db()
