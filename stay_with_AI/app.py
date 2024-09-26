from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import sqlite3
import requests
import speech_recognition as sr

app = Flask(__name__)
app.secret_key = 'supersecretkey'

FLIGHT_API_URL = 'https://19f1ebba-6edd-4769-a073-c18e12532cd1.mock.pstmn.io/flights'

# Database connection
def get_db():
    conn = sqlite3.connect('users.db')
    return conn

# Ensure that the 'bookings' table exists
def create_tables():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )''')
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

# Route for login
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email_or_username = request.form['email_or_username']
        password = request.form['password']
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, password FROM users WHERE email=? OR username=?", (email_or_username, email_or_username))
        user = cursor.fetchone()
        if user and password == user[1]:
            session['user'] = email_or_username
            session['user_id'] = user[0]  # Store user ID in session
            return redirect(url_for('index'))
        else:
            flash("Invalid login credentials")
    
    return render_template('login.html')

# Route for registration
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

# Route for the main index page
@app.route('/index', methods=['GET', 'POST'])
def index():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        origin = request.form['origin']
        destination = request.form['destination']
        return redirect(url_for('fetch_flights', origin=origin, destination=destination))

    return render_template('index.html')

# Route for fetching flights based on origin and destination
@app.route('/fetch_flights')
def fetch_flights():
    origin = request.args.get('origin')
    destination = request.args.get('destination')

    response = requests.get(FLIGHT_API_URL)
    
    if response.status_code == 200:
        flights = response.json()
        filtered_flights = [
            flight for flight in flights 
            if flight['origin'].strip().lower() == origin.strip().lower() and 
               flight['destination'].strip().lower() == destination.strip().lower()
        ]
        if filtered_flights:
            return render_template('flight_results.html', flights=filtered_flights)
        else:
            flash('No flights found for the given route')
            return redirect(url_for('index'))
    else:
        flash('Error fetching flight details')
        return redirect(url_for('index'))

# Route for booking details with speech-to-text
@app.route('/booking_details/<int:flight_id>', methods=['GET', 'POST'])
def booking_details(flight_id):
    if request.method == 'POST':
        # Call the function to collect details
        details = collect_travel_details()
        if details:
            # Handle the collected details (e.g., save to database)
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO bookings (user_id, flight_number, flight_name, origin, destination, date, full_name, contact_email, contact_phone, dob, passport, payment_info, baggage, seat, special_requests)
                              VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                           (session['user_id'], flight_id, details['flight_name'], details['departure_city'], details['destination_city'],
                            details['flight_date'], details['full_name'], details['email'], details['phone_number'], details['dob'], 
                            details['passport'], details['payment_info'], details['baggage'], details['seat'], details['special_requests']))
            conn.commit()
            conn.close()
            return redirect(url_for('booking_confirmation_list', flight_id=flight_id))
        else:
            return redirect(url_for('index'))  # Redirect to the booking page to try again

    return render_template('booking_details.html', flight_id=flight_id)

# Route for booking confirmation list
@app.route('/booking_confirmation_list/<int:flight_id>')
def booking_confirmation_list(flight_id):
    return render_template('booking_confirmation.html')  # Confirmation page

# Route for booking confirmation with booking ID
@app.route('/booking_confirmation/<int:booking_id>')
def booking_confirmation(booking_id):
    if 'user' not in session:
        return redirect(url_for('login'))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''SELECT b.flight_number, b.flight_name, b.origin, b.destination, b.date, u.username, b.full_name, b.contact_email, b.contact_phone, b.dob, b.passport, b.payment_info, b.baggage, b.seat, b.special_requests
                      FROM bookings b
                      JOIN users u ON b.user_id = u.id
                      WHERE b.id = ?''', (booking_id,))
    booking = cursor.fetchone()
    conn.close()

    if not booking:
        flash("Invalid booking ID.")
        return redirect(url_for('index'))

    return render_template('booking_confirmation.html', booking=booking)

if __name__ == '__main__':
    create_tables()
    app.run(debug=True)
