# brain/intent_router.py

class IntentRouter:
    def __init__(self):
        """
        Initialize the Intent Router.
        This will eventually load keywords, regex patterns, or a small BERT model.
        """
        self.command_keywords = [
            "open", "close", "start", "stop", "turn on", "turn off",
            "search", "play", "volume", "mute"
        ]

    def determine_intent(self, text):
        """
        Analyze text to determine if it's a COMMAND or CHAT.
        
        Args:
            text (str): User input text.
        
        Returns:
            dict: {
                "type": "COMMAND" | "CHAT",
                "confidence": float,
                "metadata": {} 
            }
        """
        text_lower = text.lower().strip()
        
        # 1. Simple Keyword Matching (Baseline)
        for keyword in self.command_keywords:
            if text_lower.startswith(keyword):
                return {
                    "type": "COMMAND",
                    "confidence": 0.8,
                    "metadata": {"keyword": keyword}
                }
        
        # 2. Default to CHAT
        return {
            "type": "CHAT",
            "confidence": 1.0,
            "metadata": {}
        }
