from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import sqlite3  # Importing sqlite3
import requests
import json

app = Flask(__name__)
app.secret_key = 'supersecretkey'

FLIGHT_API_URL = 'https://19f1ebba-6edd-4769-a073-c18e12532cd1.mock.pstmn.io/flights'

def get_db():
    conn = sqlite3.connect('users.db')
    return conn

# Ensure that the 'bookings' table exists
def create_tables():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            flight_number TEXT,
            flight_name TEXT,
            origin TEXT,
            destination TEXT,
            date TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    conn.commit()
    conn.close()

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

@app.route('/fetch_flights', methods=['POST'])
def fetch_flights():
    data = request.json
    origin = data.get('origin')
    destination = data.get('destination')

    # Debugging: Print origin and destination
    print(f"Origin: {origin}, Destination: {destination}")

    # Fetch flights from Mockaroo API
    response = requests.get(FLIGHT_API_URL)

    # Debugging: Print the status code and response
    print(f"API Status Code: {response.status_code}")
    if response.status_code == 200:
        flights = response.json()
        # Debugging: Print received flight data
        print("Flight Data from API:", flights)

        # Filter flights based on origin and destination
        filtered_flights = [flight for flight in flights if flight['origin'].lower() == origin.lower() and flight['destination'].lower() == destination.lower()]

        # Debugging: Print filtered flights
        print("Filtered Flights:", filtered_flights)

        # Return filtered flights if available, else return empty list
        return jsonify({'flights': filtered_flights})
    else:
        return jsonify({'error': 'Error fetching flight details'}), 500

# Booking route: Stores the booking into the database
@app.route('/book_flight', methods=['POST'])
def book_flight():
    if 'user' not in session:
        return redirect(url_for('login'))

    flight_data = request.json

    # Get user ID from the database
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE email=? OR username=?", (session['user'], session['user']))
    user_id = cursor.fetchone()[0]

    # Insert booking into the database
    cursor.execute('''
        INSERT INTO bookings (user_id, flight_number, flight_name, origin, destination, date)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        user_id, 
        flight_data['flight_number'], 
        flight_data['flight_name'], 
        flight_data['origin'], 
        flight_data['destination'], 
        flight_data['date']
    ))

    conn.commit()
    booking_id = cursor.lastrowid
    conn.close()

    # Redirect to confirmation page with booking ID
    return jsonify({'booking_id': booking_id})

# Booking confirmation route
@app.route('/booking_confirmation/<int:booking_id>')
def booking_confirmation(booking_id):
    if 'user' not in session:
        return redirect(url_for('login'))

    # Fetch booking details from the database
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT b.flight_number, b.flight_name, b.origin, b.destination, b.date, u.username
        FROM bookings b
        JOIN users u ON b.user_id = u.id
        WHERE b.id = ?
    ''', (booking_id,))
    booking = cursor.fetchone()
    conn.close()

    if not booking:
        flash("Invalid booking ID.")
        return redirect(url_for('index'))

    # Pass booking details to the confirmation template
    return render_template('booking_confirmation.html', booking=booking)

if __name__ == '__main__':
    create_tables()  # Ensure tables are created when the app starts
    app.run(debug=True)
