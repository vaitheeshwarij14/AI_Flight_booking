import sqlite3

conn = sqlite3.connect('users.db')
cursor = conn.cursor()

# Create a users table
cursor.execute('''CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
)''')

conn.commit()
conn.close()
