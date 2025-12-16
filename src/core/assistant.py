from src.interfaces.speech_input import ISpeechInput
from src.interfaces.speech_output import ISpeechOutput
from src.interfaces.llm_backend import ILLMBackend

class VoiceAssistant:
    def __init__(self, 
                 speech_input: ISpeechInput,
                 speech_output: ISpeechOutput,
                 llm: ILLMBackend):
        self.speech_input = speech_input
        self.speech_output = speech_output
        self.llm = llm

    def run(self) -> None:
        print("Miyori starting up...")
        while True:
            text = self.speech_input.listen()
            if text is None:
                continue
            
            # Check for exit commands (case-insensitive)
            if any(word in text.lower() for word in ['exit', 'quit', 'stop', 'goodbye']):
                self.speech_output.speak("Goodbye!")
                break
            
            # Define callback for streaming chunks - speak immediately
            def speak_chunk(chunk: str) -> None:
                self.speech_output.speak(chunk)
            
            # Use streaming for real-time TTS
            self.llm.generate_stream(text, speak_chunk)
        
        print("Miyori shutting down...")
