import sounddevice as sd
import soundfile as sf

def record_audio(filename, duration):
    print("Recording started...")
    audio_data = sd.rec(int(duration * 44100), samplerate=44100, channels=2)
    sd.wait()
    sf.write(filename, audio_data, 44100)
    print("Recording saved to", filename)

if __name__ == "__main__":
    import sys
    action = sys.argv[1]
    
    if action == "start":
        record_audio('output.wav', 10)  # 10 seconds for example
    elif action == "stop":
        print("Recording stopped.")
