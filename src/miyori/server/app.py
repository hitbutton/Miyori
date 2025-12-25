import asyncio
import threading
import time
from fastapi import FastAPI, HTTPException, BackgroundTasks
from sse_starlette.sse import EventSourceResponse
from typing import Optional

from miyori.core.state_manager import StateManager, SystemState
from miyori.core.miyori import MiyoriCore
from miyori.server.sse_manager import SSEManager
from miyori.server.models import InputRequest, StatusResponse, InputResponse
from miyori.interfaces.speech_input import ISpeechInput
from miyori.interfaces.speech_output import ISpeechOutput

app = FastAPI(title="Miyori Server")

# Global state (to be set after initialization)
state_manager: Optional[StateManager] = None
miyori_core: Optional[MiyoriCore] = None
sse_manager: Optional[SSEManager] = None
speech_output: Optional[ISpeechOutput] = None

@app.post("/input", response_model=InputResponse)
async def receive_input(request: InputRequest, background_tasks: BackgroundTasks):
    """
    Accept text input from client.
    """
    if not state_manager or not miyori_core or not sse_manager or not speech_output:
        raise HTTPException(status_code=500, detail="Server not fully initialized")

    is_text = request.source == "text"
    
    if not state_manager.can_accept_input(is_text):
        raise HTTPException(status_code=423, detail="System is busy processing")
    
    # Handle interrupt case
    if state_manager.get_state() == SystemState.SPEAKING:
        speech_output.stop()  # Cancel current audio
        state_manager.request_interrupt()
        # Wait a small amount for the interruption to propagate if needed
        await asyncio.sleep(0.1)
    
    # Transition to PROCESSING
    state_manager.transition_to(SystemState.PROCESSING)
    state_manager.clear_interrupt()
    
    # Notify clients of state change
    await sse_manager.broadcast_state(SystemState.PROCESSING)
    
    # Process in background
    background_tasks.add_task(process_request, request.text, request.source)
    
    return InputResponse(status="accepted", message="Processing input")

async def process_request(text: str, source: str):
    """Background task to process input."""
    response_chunks = []
    
    def on_chunk(chunk: str):
        # 1. Send to SSE clients
        asyncio.run_coroutine_threadsafe(sse_manager.broadcast_chunk(chunk), asyncio.get_event_loop())
        # 2. Send to speech output
        speech_output.speak(chunk)
        response_chunks.append(chunk)
    
    try:
        # Process input
        # Note: process_input is synchronous in MiyoriCore for now as it handles LLM/tools
        miyori_core.process_input(text, source, on_chunk)
        
        # Transition to SPEAKING or IDLE
        if response_chunks:
            state_manager.transition_to(SystemState.SPEAKING)
            # Use run_coroutine_threadsafe because this might be called from background thread
            asyncio.run_coroutine_threadsafe(sse_manager.broadcast_state(SystemState.SPEAKING), asyncio.get_event_loop())
            
            # Here we should ideally wait for speech to complete
            # For now, we transition to IDLE after a short delay or depend on next input
            # Actual implementation might need a callback from ISpeechOutput when done
            # simplified:
            await asyncio.sleep(0.5) 
        
    finally:
        # Return to IDLE
        state_manager.transition_to(SystemState.IDLE)
        asyncio.run_coroutine_threadsafe(sse_manager.broadcast_state(SystemState.IDLE), asyncio.get_event_loop())

@app.get("/status", response_model=StatusResponse)
async def get_status():
    """Get current system status."""
    if not state_manager or not miyori_core:
        raise HTTPException(status_code=500, detail="Server not fully initialized")
    return StatusResponse(
        state=state_manager.get_state().value,
        needs_wake_word=miyori_core.needs_wake_word()
    )

@app.get("/stream")
async def stream_events():
    """SSE endpoint for real-time updates."""
    if not sse_manager:
        raise HTTPException(status_code=500, detail="Server not fully initialized")
    return EventSourceResponse(sse_manager.event_generator())

def start_voice_thread(speech_input: ISpeechInput):
    """Start background thread for voice input."""
    def voice_loop():
        print("Voice input loop started.")
        while True:
            try:
                # Determine wake word requirement
                require_wake_word = miyori_core.needs_wake_word()
                
                # Listen for voice input
                text = speech_input.listen(require_wake_word=require_wake_word)
                
                if text is None:
                    continue
                
                # Check if we can accept voice input
                if not state_manager.can_accept_input(is_text=False):
                    print("Voice input ignored: Miyori is busy")
                    continue
                
                print(f"Voice input detected: {text}")
                
                # We need to call receive_input which is an async function
                # We can't just call it directly from this thread easily without a bridge
                # We'll use a direct call to the processing logic if possible, 
                # or use a request client, but internal call is better.
                
                asyncio.run_coroutine_threadsafe(
                    submit_voice_input_async(text),
                    asyncio.get_event_loop()
                )
            except Exception as e:
                print(f"Error in voice loop: {e}")
                time.sleep(1)
    
    thread = threading.Thread(target=voice_loop, daemon=True, name="VoiceInputThread")
    thread.start()
    return thread

async def submit_voice_input_async(text: str):
    """Bridge for voice input to the FastAPI pipeline."""
    from fastapi import BackgroundTasks
    request = InputRequest(text=text, source="voice")
    try:
        await receive_input(request, BackgroundTasks())
    except Exception as e:
        print(f"Failed to submit voice input: {e}")
