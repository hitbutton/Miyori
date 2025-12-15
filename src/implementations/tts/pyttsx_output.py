import pyttsx3
import json
from pathlib import Path
from src.interfaces.speech_output import ISpeechOutput

class PyttsxOutput(ISpeechOutput):
    def __init__(self):
        # Get config path
        # e:/_Projects/Miyori/src/implementations/tts/pyttsx_output.py
        # parent -> tts
        # parent.parent -> implementations
        # parent.parent.parent -> src
        # parent.parent.parent.parent -> Miyori
        config_path = Path(__file__).parent.parent.parent.parent / "config.json"
        
        with open(config_path, 'r') as f:
            config = json.load(f)
            
        tts_config = config.get("speech_output", {})
        rate = tts_config.get("rate", 180)
        
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', rate)

    def speak(self, text: str) -> None:
        print(f"Speaking: {text}")
        self.engine.say(text)
        self.engine.runAndWait()
