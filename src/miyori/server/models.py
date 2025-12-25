from pydantic import BaseModel
from typing import Literal

class InputRequest(BaseModel):
    text: str
    source: Literal["text", "voice"] = "text"

class InputResponse(BaseModel):
    status: str
    message: str

class StatusResponse(BaseModel):
    state: str
    needs_wake_word: bool
