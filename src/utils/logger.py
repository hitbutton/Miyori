import sys
import os
import datetime
from pathlib import Path

class Tee:
    """
    A helper class that replicates data written to a stream 
    into another stream (like the Unix 'tee' command).
    """
    def __init__(self, *streams):
        self.streams = streams

    def write(self, data):
        for stream in self.streams:
            stream.write(data)
            stream.flush()

    def flush(self):
        for stream in self.streams:
            stream.flush()

def setup_logging():
    """
    Initializes a log file in the \logs directory and redirects 
    sys.stdout and sys.stderr to it, while also maintaining output 
    to the terminal.
    """
    # Define logs directory at project root
    project_root = Path(__file__).parent.parent.parent
    logs_dir = project_root / "logs"
    
    # Create logs directory if it doesn't exist
    if not logs_dir.exists():
        os.makedirs(logs_dir)
        
    # Generate filename: Miyori_YYYYMMDD_HHMMSS_<PID>.log
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    pid = os.getpid()
    log_filename = f"Miyori_{timestamp}_{pid}.log"
    log_path = logs_dir / log_filename
    
    # Open log file in append mode (though it's a new file)
    log_file = open(log_path, "a", encoding="utf-8")
    
    # Redirect stdout and stderr using the Tee class
    sys.stdout = Tee(sys.stdout, log_file)
    sys.stderr = Tee(sys.stderr, log_file)
    
    print(f"--- Process started: {now.isoformat()} ---")
    print(f"--- Logging to: {log_path} ---")
