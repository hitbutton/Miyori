import re
import threading
import queue
import logging
from pathlib import Path
from functools import partial
import sounddevice as sd
import numpy as np
from kokoro import KPipeline
from src.interfaces.speech_output import ISpeechOutput
from src.implementations.tts.speech_pipeline import SpeechPipeline

def _kokoro_worker(q, pipeline, voice):
    """
    Worker function that runs in the background thread.
    Uses the Kokoro pipeline to generate and play audio.
    """
    logging.info("Kokoro worker started")
    
    while True:
        try:
            item = q.get()
            if item is None:
                q.task_done()
                break
            
            logging.info(f"Speaking: {item}")
            print(f"Speaking: {item}")
            
            # Generate audio
            # pipeline returns a generator of (graphemes, phonemes, audio)
            # or we can consume it all. For low latency, we might stream, 
            # but sounddevice expects a full array or a callback.
            # Let's simple-block generate first.
            
            generator = pipeline(item, voice=voice, speed=1, split_pattern=r'\n+')
            
            for i, (gs, ps, audio) in enumerate(generator):
                # audio is a numpy array (float32)
                # Sample rate is 24000 for Kokoro
                sd.play(audio, samplerate=24000)
                sd.wait() # Wait for this segment to finish
                
            q.task_done()
            
        except Exception as e:
            logging.error(f"Kokoro worker error: {e}")
            q.task_done()

class KokoroTTSOutput(ISpeechOutput):
    def __init__(self):
        # Initialize pipeline (this might download weights)
        print("Initializing Kokoro pipeline... (this may download model weights)")
        # lang_code='a' is for American English
        self.pipeline = KPipeline(lang_code='a') 
        self.voice = 'af_heart'
        
        # Get the singleton pipeline
        self._speech_pipeline = SpeechPipeline()
        
        # Configure backend
        # We need to pass the pipeline and voice to the worker
        worker_func = partial(_kokoro_worker, pipeline=self.pipeline, voice=self.voice)
        self._speech_pipeline.set_backend(worker_func)
        self._speech_pipeline.start()
        
        self._buffer = ""
        self._buffer_lock = threading.Lock()
        self._flush_timer = None
        
    def speak(self, text: str) -> None:
        """Enqueue text for speech."""
        with self._buffer_lock:
            # Cancel any pending flush
            if self._flush_timer:
                self._flush_timer.cancel()
            
            self._buffer += text
            self._process_buffer()
            
            # Schedule new flush if buffer still has content
            if self._buffer.strip():
                self._flush_timer = threading.Timer(0.5, self._flush_internal)
                self._flush_timer.start()

    def _flush_internal(self) -> None:
        """Force output of any buffered text."""
        with self._buffer_lock:
            if self._buffer.strip():
                self._speech_pipeline.enqueue(self._buffer)
            self._buffer = ""
        
    def _process_buffer(self) -> None:
        """
        Segments buffer into sentences and enqueues complete ones.
        We define a complete sentence as ending with [.!?] and followed by whitespace.
        This helps avoid splitting abbreviations like 'Dr.' immediately (though not perfect).
        """
        # Split strings where there is a sentence terminator followed by whitespace
        # (?<=[.!?]) is a lookbehind that asserts the character before the split point is . ! or ?
        # \s+ matches one or more whitespace characters
        parts = re.split(r'(?<=[.!?])\s+', self._buffer)
        
        # If we have multiple parts, it means we found split points.
        # The last part is the remainder (potentially incomplete or waiting for next space).
        # All previous parts are complete sentences (terminated and followed by space).
        if len(parts) > 1:
            for part in parts[:-1]:
                if part.strip():
                    self._speech_pipeline.enqueue(part)
            
            # The last part becomes the new buffer
            self._buffer = parts[-1]
