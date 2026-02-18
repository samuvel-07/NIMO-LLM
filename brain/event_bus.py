class EventBus:
    def __init__(self):
        self._subscribers = []

    def subscribe(self, handler):
        """
        Register an async callback function that accepts a single event dict.
        """
        self._subscribers.append(handler)

    async def emit(self, event_type: str, payload: dict):
        """
        Broadcast an event to all subscribers.
        """
        event = {
            "type": event_type,
            "payload": payload
        }
        
        for handler in self._subscribers:
            try:
                await handler(event)
            except Exception as e:
                print(f"Error in subscriber {handler}: {e}")
