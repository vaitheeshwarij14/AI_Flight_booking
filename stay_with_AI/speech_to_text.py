import speech_recognition as sr

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

# Collecting user details step-by-step
def collect_travel_details():
    details = {}

    print("Please provide the following details for your flight booking:")

    # Full Name
    details['full_name'] = listen_for_input("Please say your full name.")
    
    # Contact Information
    details['email'] = listen_for_input("Please say your email address.")
    details['phone_number'] = listen_for_input("Please say your phone number.")
    
    # Date of Birth
    details['date_of_birth'] = listen_for_input("Please say your date of birth in format day-month-year.")
    
    # Passport or ID Number
    details['passport_id'] = listen_for_input("Please say your passport or ID number.")

    # Travel Details
    details['departure_city'] = listen_for_input("Please say your departure city.")
    details['destination_city'] = listen_for_input("Please say your destination city.")
    details['flight_date'] = listen_for_input("Please say the date of your flight in format day-month-year.")
    
    # Payment Information
    details['payment_method'] = listen_for_input("Please say your preferred payment method, such as credit card or PayPal.")
    
    # Baggage Preferences
    details['baggage_info'] = listen_for_input("Do you want extra baggage? Please say yes or no.")
    
    # Seat Preference
    details['seat_preference'] = listen_for_input("Please say your seat preference: window, aisle, or middle.")
    
    # Special Requests
    details['special_requests'] = listen_for_input("Do you have any special requests, like meal preferences or assistance?")
    
    # Confirm flight details
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

if __name__ == "__main__":
    collect_travel_details()
