# Text-to-Speech Implementation Plan

## Step 1: Set up the file
- Create `pyttsx_output.py` in this directory
- Import required modules: `pyttsx3`, `json`, `pathlib.Path`, `ISpeechOutput` from interfaces

## Step 2: Define the class
```python
class PyttsxOutput(ISpeechOutput):
```

## Step 3: Implement __init__
```python
def __init__(self):
    # Get config path: Path(__file__).parent.parent.parent / "config.json"
    # Open and load config.json
    # Extract speech_output config section
    # Create self.engine = pyttsx3.init()
    # Set rate: self.engine.setProperty('rate', rate_from_config)
```

## Step 4: Implement speak()
```python
def speak(self, text: str) -> None:
    # Print f"Speaking: {text}"
    # self.engine.say(text)
    # self.engine.runAndWait()
```

## Interface Contract
```python
class ISpeechOutput(ABC):
    @abstractmethod
    def speak(self, text: str) -> None:
        """Convert text to speech"""
```

## Config Keys (from config.json)
```json
{
  "speech_output": {
    "rate": 180
  }
}
```

## Notes
- `rate` = words per minute (default 180, range typically 100-300)
- Engine is reusable, initialize once in constructor
- Use `Path(__file__).parent.parent.parent / "config.json"` for robust path resolution