import sys
import os

# Add project root to path so we can import src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.implementations.speech.google_speech_input import GoogleSpeechInput

def test_speech():
    print("Initializing GoogleSpeechInput...")
    try:
        speech_input = GoogleSpeechInput()
    except Exception as e:
        print(f"Failed to initialize speech input: {e}")
        return

    print("\n--- Speech Test ---")
    print("Please speak into your microphone...")
    
    result = speech_input.listen()
    
    print("-" * 20)
    if result:
        print(f"Recognized: {result}")
    else:
        print("No speech detected or error occurred.")
    print("Speech Test Completed.")

if __name__ == "__main__":
    test_speech()
