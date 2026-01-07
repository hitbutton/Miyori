# Skill: Voice & Speech Processing

This skill covers Miyori's voice-first interface, including wake-word detection, speech-to-text (STT), and text-to-speech (TTS).

## 1. Speech Input (`PorcupineCobraVosk`)
Uses a hybrid approach for low-latency voice detection and transcription.

### Pipeline:
1. **Wake Word (Porcupine)**: Constantly monitors the audio stream for the "Miyori" (or configured) wake word.
2. **Voice Activity Detection (Cobra)**: Once awake, it uses Cobra to determine when the user is actually speaking versus background noise.
    - **Hysteresis**: High threshold to start listening, lower threshold to maintain the "speaking" state.
    - **Grace Period**: Waits for a short period of silence before finalizing the recording.
3. **Transcription (Vosk)**: Locally transcribes the recorded PCM frames into text.

### Implementation Details:
- **Location**: `src/miyori/implementations/speech/porcupine_cobra_vosk.py`
- **Sample Rate**: Determined by the Porcupine engine (usually 16kHz).
- **Control Flow**: Managed by `MiyoriCore.process_input` which checks if a wake word is needed based on interaction timeouts.

## 2. Speech Output (`KokoroTTSOutput`)
Generates high-quality, human-like voice responses.

### Pipeline:
1. **Speech Pipeline**: A background worker thread that handles the text queue.
2. **Synthesis (Kokoro)**: Uses the Kokoro model (`af_heart` voice) to generate audio chunks from text.
3. **Playback (Sounddevice)**: An asynchronous output stream plays audio chunks via a callback mechanism.

### Features:
- **Streaming Speech**: Can start speaking as soon as the first sentence/chunk is synthesized.
- **Punctuation Parsing**: The `SpeechPipeline` splits long text into natural phrases to improve flow.
- **Voice Parameters**: Optimized at 1.25x speed for a natural, conversational rhythm.

### Implementation Details:
- **Location**: `src/miyori/implementations/tts/kokoro_tts_output.py`
- **Sample Rate**: 24kHz.
- **Buffer Logic**: Aggregates short chunks of text and flushes them to the synthesizer using a short timer (0.5s) to ensure smooth delivery.

## 3. Best Practices for Voice
- **Natural Punctuation**: Use commas and periods to create pauses in the TTS engine.
- **Discourse Markers**: Start responses with words like "Well," "Actually," or "Honestly" to sound more human-like during voice interactions.
- **Phonetic Handling**: Be aware of words that STT might mishear or TTS might mispronounce.
