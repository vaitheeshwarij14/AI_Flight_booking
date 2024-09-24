from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import sqlite3
import requests
import json
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

# Function to listen for user input
def listen_for_input(prompt_text):
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    
    print(prompt_text)
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        response = recognizer.recognize_google(audio)
        print(f"You said: {response}")
        return response
    except sr.UnknownValueError:
        print("Sorry, I could not understand your speech.")
        return None
    except sr.RequestError:
        print("Error with the speech recognition service.")
        return None

# Function to collect flight booking details via speech-to-text
def collect_travel_details():
    print("Please provide the following details for your flight booking:")
    details = {}

    details['full_name'] = listen_for_input("Please say your full name.")
    details['email'] = listen_for_input("Please say your email address.")
    details['phone_number'] = listen_for_input("Please say your phone number.")
    details['dob'] = listen_for_input("Please say your date of birth in format day-month-year.")
    details['passport'] = listen_for_input("Please say your passport or ID number.")
    details['departure_city'] = listen_for_input("Please say your departure city.")
    details['destination_city'] = listen_for_input("Please say your destination city.")
    details['flight_date'] = listen_for_input("Please say the date of your flight in format day-month-year.")
    details['payment_info'] = listen_for_input("Please say your preferred payment method, such as credit card or PayPal.")
    details['baggage'] = listen_for_input("Do you want extra baggage? Please say yes or no.")
    details['seat'] = listen_for_input("Please say your seat preference: window, aisle, or middle.")
    details['special_requests'] = listen_for_input("Do you have any special requests, like meal preferences or assistance?")

    # Confirm details
    print("\nPlease confirm the following details:")
    for key, value in details.items():
        print(f"{key.replace('_', ' ').title()}: {value}")

    confirmation = listen_for_input("Is all the information correct? Please say yes or no.")
    if confirmation and confirmation.lower() == "yes":
        print("Booking confirmed!")
        return details
    else:
        print("Please restart the process to correct the details.")
        return None

# Route for login
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
@app.route('/index')
def index():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

# Route for logout
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

# Route for fetching flights
@app.route('/fetch_flights', methods=['POST'])
def fetch_flights():
    data = request.json
    origin = data.get('origin')
    destination = data.get('destination')

    response = requests.get(FLIGHT_API_URL)
    
    if response.status_code == 200:
        flights = response.json()
        filtered_flights = [
            flight for flight in flights 
            if flight['origin'].strip().lower() == origin.strip().lower() and 
               flight['destination'].strip().lower() == destination.strip().lower()
        ]
        if filtered_flights:
            return jsonify({'flights': filtered_flights})
        else:
            return jsonify({'message': 'No flights found for the given route'}), 404
    else:
        return jsonify({'error': 'Error fetching flight details'}), 500

# Route for booking details with speech-to-text
@app.route('/booking_details/<int:flight_id>', methods=['GET', 'POST'])
def booking_details(flight_id):
    if request.method == 'POST':
        # Call the function to collect details
        details = collect_travel_details()
        if details:
            # Handle the collected details (e.g., save to database, send confirmation)
            return redirect(url_for('booking_confirmation_list', flight_id=flight_id))
        else:
            return redirect(url_for('index'))  # Redirect to the booking page to try again

    return render_template('booking_details.html', flight_id=flight_id)

@app.route('/booking_confirmation_list')
def booking_confirmation_list():
    return render_template('booking_confirmation.html')  # Confirmation page

# Route for recording details
@app.route('/recording_details/<int:flight_id>', methods=['GET'])
def recording_details(flight_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('recording_details.html', flight_id=flight_id)

# Route for submitting recorded details
@app.route('/submit_recording/<int:flight_id>', methods=['POST'])
def submit_recording(flight_id):
    if 'user' not in session:
        return redirect(url_for('login'))

    recorded_text = request.form.get('recorded_text')
    
    # Process the recorded text and extract details
    # For now, just print it to the console
    print(f"Recorded details for Flight {flight_id}: {recorded_text}")

    # You can implement logic to parse the recorded text and save the details
    # or redirect to a confirmation page.
    
    return redirect(url_for('booking_confirmation_list'))

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
