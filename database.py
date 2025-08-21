import sqlite3

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Create treatments table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS treatments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            userId INTEGER NOT NULL,
            petId TEXT NOT NULL,
            petName TEXT NOT NULL,
            petType TEXT NOT NULL,
            treatmentType TEXT NOT NULL,
            description TEXT,
            date TEXT NOT NULL,
            timeSlot TEXT NOT NULL,
            vetName TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()
    print("✅ Database initialized and treatments table is ready!")

if __name__ == "__main__":
    init_db()