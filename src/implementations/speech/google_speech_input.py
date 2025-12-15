import speech_recognition as sr
import json
from pathlib import Path
from src.interfaces.speech_input import ISpeechInput

class GoogleSpeechInput(ISpeechInput):
    def __init__(self):
        # Get config path: Path(__file__).parent.parent.parent / "config.json"
        # This resolves to e:/_Projects/Miyori/src/implementations/speech/../../../config.json -> e:/_Projects/Miyori/config.json
        config_path = Path(__file__).parent.parent.parent.parent / "config.json"
        
        with open(config_path, 'r') as f:
            config = json.load(f)
            
        speech_config = config.get("speech_input", {})
        
        self.recognizer = sr.Recognizer()
        self.recognizer.pause_threshold = speech_config.get("pause_threshold", 2.0)
        self.recognizer.energy_threshold = speech_config.get("energy_threshold", 300)

    def listen(self) -> str | None:
        try:
            with sr.Microphone() as source:
                print("Calibrating microphone...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                print("Listening...")
                audio = self.recognizer.listen(source)
                print("Processing...")
                text = self.recognizer.recognize_google(audio)
                print(f"You said: {text}")
                return text
        except Exception as e:
            # Plan says "If any exception occurs, return None" and "No error handling (let exceptions bubble up)"
            # Wait, plan says "If any exception occurs, return None" in step 4.
            # But Design Rules #2 says "No error handling this phase (let exceptions bubble up)".
            # I will follow Step 4 explicitly: "If any exception occurs, return None" seems to contradict "let bubbles up" if we catch generic Exception.
            # However, `recognize_google` raises UnknownValueError if unintelligible. Returning None is better for the loop.
            # Let's follow the code snippet logic in the plan if it was explicit.
            # Plan Step 4: "# If any exception occurs, return None"
            # So I will catch and return None.
            # print(f"Error listening: {e}")
            return None
