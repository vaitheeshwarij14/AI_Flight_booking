import speech_recognition as sr
import tkinter as tk
from tkinter import messagebox
import threading

# Initialize recognizer
recognizer = sr.Recognizer()

# Global flag to control when to stop listening
listening = False

# Function to capture audio from the microphone and convert it to text
def capture_and_convert_speech():
    global listening
    listening = True  # Start listening
    
    with sr.Microphone() as source:
        print("Please say something...")

        # Adjust the recognizer sensitivity to ambient noise
        recognizer.adjust_for_ambient_noise(source)

        # Capture audio from the microphone until stop is clicked
        try:
            while listening:
                print("Listening...")
                result_label.config(text="Listening...")  # Update label to show status
                root.update()  # Update the GUI to reflect the status

                # Listen for audio input (this call waits for the user to finish talking)
                audio = recognizer.listen(source)

                # Recognize speech using Google Web Speech API
                try:
                    text = recognizer.recognize_google(audio)
                    print("You said: " + text)
                    result_label.config(text="You said: " + text)  # Update the label with the recognized text
                except sr.UnknownValueError:
                    result_label.config(text="Sorry, I could not understand the audio.")
                except sr.RequestError as e:
                    result_label.config(text=f"Could not request results; {e}")

                # Stop automatically after one successful recognition
                listening = False
        except Exception as e:
            result_label.config(text=f"Error: {e}")

# Function to start recording
def start_recording():
    global listening
    if not listening:  # Check if already listening to avoid restarting the process
        listening = True  # Enable listening
        result_label.config(text="Ready to listen... Click 'Stop' to finish.")
        root.update()  # Update the GUI immediately

        # Start a thread for listening in the background
        threading.Thread(target=capture_and_convert_speech).start()
    else:
        result_label.config(text="Already listening...")

# Function to stop recording
def stop_recording():
    global listening
    listening = False  # Disable listening
    result_label.config(text="Recording stopped.")
    root.update()

# Create the main window
root = tk.Tk()
root.title("Voice to Text Converter")
root.geometry("400x250")

# Create a label for the instructions
instruction_label = tk.Label(root, text="Click 'Start Recording' to begin, and 'Stop' to finish:")
instruction_label.pack(pady=10)

# Create a frame to hold the buttons
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

# Create a button to start recording
start_button = tk.Button(button_frame, text="Start Recording", command=start_recording, width=15)
start_button.grid(row=0, column=0, padx=10)

# Create a button to stop recording
stop_button = tk.Button(button_frame, text="Stop Recording", command=stop_recording, width=15)
stop_button.grid(row=0, column=1, padx=10)

# Create a label to display the result
result_label = tk.Label(root, text="", wraplength=300)
result_label.pack(pady=10)

# Start the GUI loop
root.mainloop()
