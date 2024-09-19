from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3  # Make sure to import sqlite3

app = Flask(__name__)
app.secret_key = 'supersecretkey'

def get_db():
    conn = sqlite3.connect('users.db')
    return conn

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email_or_username = request.form['email_or_username']
        password = request.form['password']
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE email=? OR username=?", (email_or_username, email_or_username))
        user = cursor.fetchone()
        if user and password == user[0]:
            session['user'] = email_or_username
            return redirect(url_for('index'))
        else:
            flash("Invalid login credentials")
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", (username, email, password))
        conn.commit()
        flash("Registration successful! Please log in.")
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/index')
def index():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
