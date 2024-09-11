import speech_recognition as sr

# Initialize recognizer
recognizer = sr.Recognizer()

# Function to capture audio from the microphone and convert it to text
def capture_and_convert_speech():
    with sr.Microphone() as source:
        print("Please say something...")
        # Adjust the recognizer sensitivity to ambient noise
        recognizer.adjust_for_ambient_noise(source)
        # Capture audio from the microphone
        audio = recognizer.listen(source)

        try:
            # Recognize speech using Google Web Speech API
            text = recognizer.recognize_google(audio)
            print("You said: " + text)
            return text
        except sr.UnknownValueError:
            print("Sorry, I could not understand the audio.")
            return None
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
            return None

# Call the function
capture_and_convert_speech()

# to do     to recognoise the completion of the speech need a stop word to be coded in here --> working on it
