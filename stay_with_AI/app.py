from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import subprocess  # To trigger the Python voice recorder script
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Connect to SQLite database
def get_db():
    conn = sqlite3.connect('users.db')
    return conn

# Route for the login page
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email_or_username = request.form['email_or_username']
        password = request.form['password']
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE email=? OR username=?", (email_or_username, email_or_username))
        user = cursor.fetchone()
        if user and check_password_hash(user[0], password):
            session['user'] = email_or_username
            return redirect(url_for('index'))
        else:
            flash("Invalid login credentials")
    
    return render_template('login.html')

# Route for the registration page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", (username, email, password))
        conn.commit()
        flash("Registration successful! Please log in.")
        return redirect(url_for('login'))

    return render_template('register.html')

# Route for the main page
@app.route('/index')
def index():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

# Route to start/stop the voice recording
@app.route('/start_recording', methods=['POST'])
def start_recording():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'start':
            subprocess.Popen(["python", "voice_recorder.py", "start"])
        elif action == 'stop':
            subprocess.Popen(["python", "voice_recorder.py", "stop"])
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
