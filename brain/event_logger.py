import json
import time
from pathlib import Path

class EventLogger:

    def __init__(self, log_file="brain_events.log"):
        # Ensure log file is in the project root or relative to execution
        self.log_path = Path(log_file)

    async def handle_event(self, event: dict):
        event["timestamp"] = time.time() # Ensure timestamp matches emission time if not present? 
        # Actually orchestration doesn't add timestamp in emit payload usually.
        # Let's add it here if missing, or better, EventBus could add it?
        # User prompt says: 
        # event = { "type": event_type, "payload": payload } in EventBus
        # And Logger writes: json.dumps(event)
        
        # Let's add timestamp here for consistency with previous logger
        if "timestamp" not in event:
             event["timestamp"] = time.time()

        try:
            with self.log_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(event) + "\n")
        except Exception as e:
            print(f"Failed to log event: {e}")
