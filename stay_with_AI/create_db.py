import sqlite3

def create_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        email TEXT UNIQUE,
        password TEXT
    )''')

    # Create bookings table
    cursor.execute('''CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        flight_number TEXT,
        flight_name TEXT,
        origin TEXT,
        destination TEXT,
        date TEXT,
        full_name TEXT,
        contact_email TEXT,
        contact_phone TEXT,
        dob TEXT,
        passport TEXT,
        payment_info TEXT,
        baggage TEXT,
        seat TEXT,
        special_requests TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')

    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_db()
