import struct
import pvcobra
import pyaudio
import pvporcupine
import speech_recognition as sr
from collections import deque
from src.interfaces.speech_input import ISpeechInput
from src.utils.config import Config

class HorribleSpeechInput(ISpeechInput):
    def __init__(self):
        speech_config = Config.data.get("speech_input", {})
        self.access_key = speech_config.get("porcupine_access_key")
        
        if not self.access_key:
            raise ValueError("Access key not found in config.json")

        # 1. Initialize Engines
        # Use the same sample rate for everything (Picovoice engines use 16kHz)
        self.porcupine = self._init_porcupine(speech_config)
        self.cobra = pvcobra.create(access_key=self.access_key)
        
        self.sample_rate = self.porcupine.sample_rate # 16000
        self.frame_length = self.porcupine.frame_length # 512
        
        # 2. Setup Audio Stream
        self.pa = pyaudio.PyAudio()
        self.audio_stream = self.pa.open(
            rate=self.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=self.frame_length
        )

        # 3. Utilities
        self.recognizer = sr.Recognizer()
        # Pre-roll buffer to catch the start of sentences (approx 0.5 seconds)
        self.pre_roll_count = 15 
        self.pre_roll_buffer = deque(maxlen=self.pre_roll_count)

    def _init_porcupine(self, config):
        keyword_paths = config.get("keyword_paths", [])
        keywords = config.get("keywords", ["porcupine"])
        if keyword_paths:
            return pvporcupine.create(access_key=self.access_key, keyword_paths=keyword_paths)
        return pvporcupine.create(access_key=self.access_key, keywords=keywords)

    def listen(self, require_wake_word: bool = True) -> str | None:
        """
        Uses Porcupine for wake-word, Cobra for VAD, and Google for ASR.
        """
        try:
            # --- PHASE 1: WAKE WORD DETECTION ---
            if require_wake_word:
                print("[Status] Waiting for wake word...")
                while True:
                    pcm = self._read_frame()
                    self.pre_roll_buffer.append(pcm) # Always keep a bit of history
                    if self.porcupine.process(pcm) >= 0:
                        print("[Status] Wake word detected!")
                        break

            # --- PHASE 2: VOICE ACTIVITY DETECTION (COBRA) ---
            print("[Status] Listening for command...")
            recording_buffer = list(self.pre_roll_buffer) # Start with the pre-roll history
            
            is_speaking = False
            silence_frames = 0
            max_silence = 25  # ~0.8 seconds of silence to trigger end-of-speech
            max_recording_time = 15 * (self.sample_rate / self.frame_length) # 15 sec limit

            for _ in range(int(max_recording_time)):
                pcm = self._read_frame()
                recording_buffer.append(pcm)
                
                # Cobra returns a probability (0.0 to 1.0)
                voice_probability = self.cobra.process(pcm)
                
                if voice_probability > 0.6: # Threshold for "speech"
                    if not is_speaking:
                        is_speaking = True
                    silence_frames = 0
                elif is_speaking:
                    silence_frames += 1
                
                # Exit loop if user stops talking
                if is_speaking and silence_frames > max_silence:
                    print("[Status] End of speech detected.")
                    break
            else:
                print("[Status] Recording timed out.")

            
            if not is_speaking:
                return None

            return self._transcribe(recording_buffer)

        except Exception as e:
            print(f"Error in listen: {e}")
            return None

    def _read_frame(self):
        """Reads and unpacks a single audio frame."""
        data = self.audio_stream.read(self.frame_length, exception_on_overflow=False)
        return struct.unpack_from("h" * self.frame_length, data)

    def _transcribe(self, pcm_frames):
        """Converts PCM list to AudioData and sends to Google."""
        print("[Status] Transcribing...")
        # Flatten the list of frames and convert to bytes
        flat_pcm = [item for frame in pcm_frames for item in frame]
        audio_bytes = struct.pack("h" * len(flat_pcm), *flat_pcm)
        
        audio_data = sr.AudioData(audio_bytes, self.sample_rate, 2) # 2 bytes for 16-bit
        
        try:
            text = self.recognizer.recognize_google(audio_data)
            print(f"Result: {text}")
            return text
        except sr.UnknownValueError:
            print("Google could not understand audio.")
        except sr.RequestError as e:
            print(f"Google API error: {e}")
        return None

    def __del__(self):
        if hasattr(self, 'porcupine'): self.porcupine.delete()
        if hasattr(self, 'cobra'): self.cobra.delete()
        if hasattr(self, 'audio_stream'): self.audio_stream.close()
        if hasattr(self, 'pa'): self.pa.terminate()