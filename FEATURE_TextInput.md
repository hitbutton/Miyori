## 1. Architectural Foundation: The Stateful Server
The core logic will be decoupled from the I/O interfaces and wrapped in a service (via FastAPI). This allows the "Brain" to remain active and responsive to external requests even while specific hardware interfaces are busy or blocking.

### State Management
The system will operate as a **State Machine** to govern how it handles concurrent inputs:
* **IDLE:** The system is waiting. Both voice and text inputs are accepted.
* **PROCESSING:** The LLM is generating a response or executing tools. New inputs are rejected with a "Busy" signal.
* **SPEAKING:** The system is playing audio output. Text input is allowed to interrupt and cancel current playback.

---

## 2. Input Handling Strategy
Inputs are categorized by priority and source, moving away from a single-threaded queue in favor of a **Signal-Driven** approach.

### Text Input (High Priority / Interrupt)
* **Access:** Exposed via an API endpoint (e.g., `POST /input`).
* **Interruption Logic:** If a text request arrives during the **SPEAKING** state, the server issues a "Stop" command to the audio interface immediately and switches to **PROCESSING** the new text.
* **Rejection Logic:** If the server is in the **PROCESSING** state, the API returns a failure code (e.g., 423 Locked). This allows the client UI to provide immediate feedback (like flashing the input box red) and retain the user's text for a retry.

### Voice Input (Ambient / Background)
* **Threading:** The `listen()` method is moved to a dedicated background thread to prevent it from blocking the server's main process.
* **Submission:** When `listen()` returns a result, it attempts to submit the text to the core logic. 
* **Validation:** The core only accepts voice results if the current state is **IDLE**. If the system has moved to another state (due to a text interrupt), the voice result is discarded.



---

## 3. Project Structure and Packaging
The project will follow the `src` layout compatible with `uv` packaging, facilitating multiple entry points.

* **Core Logic:** Located in `src/miyori/`, containing the state manager, tool registry, and backend interfaces.
* **Server Entry Point:** A script to launch the FastAPI service.
* **Client Entry Points:** Separate scripts for the Terminal UI or GUI that communicate with the server via HTTP/WebSockets.
* **Inter-Process Communication:** For single-machine use, the UI and Server can remain in the same environment but communicate over a local port, ensuring the GUI remains responsive regardless of the AI's internal processing state.

---

## 4. Execution Flow
1.  **Startup:** The server initializes the `MiyoriCore`, starts the background `SpeechInput` thread, and opens the API.
2.  **Listening:** `SpeechInput` blocks until audio is detected.
3.  **Command Reception:**
    * If **Voice** returns text: It is processed if the state is **IDLE**.
    * If **Text** is posted: It is processed if the state is **IDLE** or **SPEAKING** (interrupting the latter).
4.  **Response:** The LLM generates text; the `SpeechOutput` interface streams the audio.
5.  **Reset:** Once audio finishes, the system returns to **IDLE**.