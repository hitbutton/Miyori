import json
import re
import logging
import threading
from pathlib import Path
from functools import partial
from src.interfaces.speech_output import ISpeechOutput
from src.implementations.tts.speech_pipeline import SpeechPipeline

def _pyttsx_worker(q, rate):
    """
    Worker function that runs in the background thread.
    Owns the pyttsx3 engine instance and keeps a persistent event loop.
    """
    import pyttsx3
    import time
    import queue
    import uuid
    
    try:
        # Initialize engine only once in this thread
        engine = pyttsx3.init()
        engine.setProperty('rate', rate)
        
        # Setup callback for task completion
        def on_finished(name, completed):
            try:
                q.task_done()
            except ValueError:
                pass
                
        engine.connect('finished-utterance', on_finished)
        
        # Start the loop without blocking
        engine.startLoop(False)
        logging.info(f"pyttsx3 initialized with rate={rate} in persistent loop mode")
        
        while True:
            # Pump the engine's event loop
            engine.iterate()
            
            # Check for new items without blocking the loop
            try:
                item = q.get_nowait()
                if item is None:
                    # Poison pill
                    q.task_done()
                    break
                
                logging.info(f"Speaking: {item}")
                print(f"Speaking: {item}")
                engine.say(item, name=str(uuid.uuid4()))
                
            except queue.Empty:
                # Small sleep to prevent 100% CPU usage while idle
                time.sleep(0.01)
                
        # Clean up
        engine.endLoop()
        
    except Exception as e:
        logging.error(f"pyttsx3 worker crashed: {e}")
        # Ensure we don't leave the queue hanging if we crash
        try:
             while True:
                 q.get_nowait()
                 q.task_done()
        except:
             pass

class PyttsxOutput(ISpeechOutput):
    """
    Pyttsx3 implementation of ISpeechOutput.
    Delegates actual work to the centralized SpeechPipeline.
    """
    def __init__(self):
        # Determine config path (relative to this file)
        # src/implementations/tts/pyttsx_output.py -> ... -> config.json
        config_path = Path(__file__).parent.parent.parent.parent / "config.json"
        
        self._buffer = ""
        self._buffer_lock = threading.Lock()
        self._flush_timer = None
        
        rate = 180
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                tts_config = config.get("speech_output", {})
                rate = tts_config.get("rate", 180)
            except Exception as e:
                logging.warning(f"Could not load TTS config: {e}. Using default.")
        
        # Get the singleton pipeline
        self.pipeline = SpeechPipeline()
        
        # Configure and start if not already running
        # We pass the partial function with the config loaded 
        # (this only takes effect if set_backend is successful, i.e. first caller)
        worker_func = partial(_pyttsx_worker, rate=rate)
        self.pipeline.set_backend(worker_func)
        self.pipeline.start()

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
                self.pipeline.enqueue(self._buffer)
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
                    self.pipeline.enqueue(part)
            
            # The last part becomes the new buffer
            self._buffer = parts[-1]
