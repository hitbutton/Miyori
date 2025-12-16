import sys
import os

# Add project root to path so we can import src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.implementations.tts.pyttsx_output import PyttsxOutput

def test_tts():
    print("Initializing PyttsxOutput...")
    try:
        tts = PyttsxOutput()
    except Exception as e:
        print(f"Failed to initialize TTS: {e}")
        return

    text = "This is a test of the text to speech system. Miyori is online."
    print(f"\nSpeaking: '{text}'")
    
    try:
        tts.speak(text)
        print("TTS Test Completed.")
    except Exception as e:
        print(f"Error during TTS: {e}")

if __name__ == "__main__":
    test_tts()
