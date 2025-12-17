from src.implementations.speech.porcupine_speech_input import PorcupineSpeechInput
from src.implementations.tts.pyttsx_output import PyttsxOutput
from src.implementations.llm.google_ai_backend import GoogleAIBackend
from src.core.assistant import VoiceAssistant

def main():
    speech_input = PorcupineSpeechInput()
    speech_output = PyttsxOutput()
    llm_backend = GoogleAIBackend()
    
    assistant = VoiceAssistant(speech_input, speech_output, llm_backend)
    assistant.run()

if __name__ == "__main__":
    main()
