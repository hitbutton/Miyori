from src.implementations.speech.porcupine_speech_input import PorcupineSpeechInput
from src.implementations.tts.kokoro_tts_output import KokoroTTSOutput
from src.implementations.llm.google_ai_backend import GoogleAIBackend
from src.core.assistant import VoiceAssistant

def main():
    speech_input = PorcupineSpeechInput()
    speech_output = KokoroTTSOutput()
    llm_backend = GoogleAIBackend()
    
    assistant = VoiceAssistant(speech_input, speech_output, llm_backend)
    assistant.run()

if __name__ == "__main__":
    main()
