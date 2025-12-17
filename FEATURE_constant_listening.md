# Porcupine Wake Word Integration Plan

Refactor the speech input pipeline to support continuous listening with a custom wake word ("hey miyori") using Porcupine, falling back to Google ASR for command transcription.

## User Review Required

> [!IMPORTANT]
> **Porcupine Access Key Required**: You must provide a valid Picovoice AccessKey in `config.json` under `speech_input.porcupine_access_key`.
> **Custom Keyword File**: To use "hey miyori", you must provide the path to the `.ppn` file in `speech_input.keyword_paths`. If not provided, it will default to the built-in 'porcupine' keyword for testing.

## Proposed Changes

### Configuration
1.  **Modify `config.json`** (and example):
    -   Add `porcupine_access_key`: String (Required).
    -   Add `keyword_paths`: List[String] (Optional, for custom `.ppn` files).
    -   Add `keywords`: List[String] (Optional, for built-in keywords like 'porcupine').

### Dependencies
1.  **Modify `requirements.txt`**:
    -   Add `pvporcupine`.

### Source Code
1.  **Create `src/implementations/speech/porcupine_speech_input.py`**:
    -   Implements `ISpeechInput`.
    -   **Init**:
        -   Initialize `pvporcupine` with key and keywords.
        -   Initialize `pyaudio` stream (16kHz, mono).
        -   Initialize `speech_recognition.Recognizer`.
    -   **Listen**:
        -   **Loop A (Wake Word)**: Read 512-sample frames from PyAudio, feed to Porcupine.
        -   **Trigger**:
            -   Log "Wake word detected".
            -   Enter **Loop B (Capture)**.
        -   **Loop B (Capture)**:
            -   Continue reading frames.
            -   Calculate RMS amplitude for Voice Activity Detection (VAD).
            -   Buffer audio data.
            -   Stop when silence duration > `pause_threshold`.
        -   **Transcribe**:
            -   Convert buffered bytes to `sr.AudioData`.
            -   Call `recognizer.recognize_google(audio_data)`.
            -   Return text.

2.  **Modify `main.py`**:
    -   Import `PorcupineSpeechInput`.
    -   Replace `GoogleSpeechInput` instantiation with `PorcupineSpeechInput`.

### Testing
1.  **Modify `tests/test_speech.py`**:
    -   Update to instantiate `PorcupineSpeechInput` to verify the wake word functionality.

## Verification Plan

### Automated
- Run `tests/test_speech.py`.
    -   **Expectation**: The potential script waits silently.
    -   **Action**: User says wake word ("Porcupine" or "Hey Miyori").
    -   **Expectation**: Script prints "Wake word detected" (or similar log), then listens for command.
    -   **Action**: User says "Hello World".
    -   **Expectation**: Script prints "Recognized: Hello World".

### Manual
- Run `main.py`.
    -   Verify the assistant loop works with the new wake word mode.
    -   Check for CPU usage (Porcupine is very efficient).
    -   Check for latency (should be instant transition from wake word to recording).
