import sqlite3
from flask import Flask, render_template, request, redirect, url_for, jsonify

app = Flask(__name__)

# Function to create the 'users' table if it doesn't exist
def create_users_table():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 username TEXT NOT NULL,
                 email TEXT NOT NULL UNIQUE,
                 password TEXT NOT NULL)''')
    conn.commit()
    conn.close()

# Ensure the table is created when the application starts
create_users_table()

# Sample Python function to run when "Speak" button is clicked
def generate_text():
    return "This is the AI speaking!"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # Insert the user data into the database
        conn = sqlite3.connect('users.db')
        c = conn.cursor()

        try:
            c.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)', 
                      (username, email, password))
            conn.commit()
        except sqlite3.IntegrityError:
            # Handle unique constraint violation (duplicate email)
            return "Error: Email already exists!"
        finally:
            conn.close()
        
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Validate user credentials
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE email = ? AND password = ?', (email, password))
        user = c.fetchone()
        conn.close()
        
        if user:
            return redirect(url_for('home', username=user[1]))  # Redirect to home with username
        else:
            return "Invalid email or password!"
    
    return render_template('login.html')

@app.route('/home/<username>')
def home(username):
    return render_template('home.html', username=username)

# Endpoint for the Speak button (Optional, unused now)
@app.route('/speak', methods=['POST'])
def speak():
    text = generate_text()
    return jsonify({'text': text})

if __name__ == '__main__':
    app.run(debug=True)
