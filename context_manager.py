# context_manager.py
"""
Context Memory for JARVIS
Remembers past commands and handles references like "it", "that", "again"
"""
from datetime import datetime
from collections import deque

class ContextManager:
    def __init__(self, max_history=15):
        self.history = deque(maxlen=max_history)
        self.last_app_opened = None
        self.last_app_closed = None
        self.last_media_played = None
        self.last_search_term = None
        self.session_start = datetime.now()
        self.command_count = 0
    
    def add_interaction(self, command, intent_data, response, success=True):
        """
        Store interaction in history
        """
        interaction = {
            "timestamp": datetime.now(),
            "command": command,
            "intent": intent_data.get("intent"),
            "entities": intent_data.get("entities", {}),
            "response": response,
            "success": success
        }
        self.history.append(interaction)
        self.command_count += 1
        
        # Update context variables for quick reference
        if success:
            intent = intent_data.get("intent")
            entities = intent_data.get("entities", {})
            
            if intent == "open_app" and "app_name" in entities:
                self.last_app_opened = entities["app_name"]
            
            elif intent == "close_app" and "app_name" in entities:
                self.last_app_closed = entities["app_name"]
            
            elif intent == "play_media" and "media_name" in entities:
                self.last_media_played = entities["media_name"]
            
            elif intent == "search_query" and "search_term" in entities:
                self.last_search_term = entities["search_term"]
    
    def resolve_reference(self, command):
        """
        Handle pronouns and references:
        - "close it" → "close chrome" (if chrome was last opened)
        - "play it again" → "play [last song]"
        - "do that again" → repeat last command
        """
        command_lower = command.lower()
        
        # Handle "again" or "repeat"
        if any(word in command_lower for word in ["again", "repeat"]):
            if self.history:
                last_cmd = self.history[-1]["command"]
                return last_cmd
            return command
        
        # Handle "it" or "that" references
        if any(ref in command_lower for ref in [" it", " that", "the app", "the same"]):
            
            # If command is about closing something
            if any(word in command_lower for word in ["close", "quit", "exit", "kill"]):
                if self.last_app_opened:
                    command = self._replace_reference(command, self.last_app_opened)
            
            # If command is about opening something  
            elif any(word in command_lower for word in ["open", "launch", "start"]):
                if self.last_app_closed:
                    command = self._replace_reference(command, self.last_app_closed)
            
            # If command is about playing media
            elif any(word in command_lower for word in ["play"]):
                if self.last_media_played:
                    command = self._replace_reference(command, self.last_media_played)
        
        return command
    
    def _replace_reference(self, command, replacement):
        """Replace pronouns with actual references"""
        command = command.replace(" it", f" {replacement}")
        command = command.replace(" that", f" {replacement}")
        command = command.replace("the app", replacement)
        command = command.replace("the same", replacement)
        return command
    
    def get_last_interaction(self):
        """Get most recent interaction"""
        return self.history[-1] if self.history else None
    
    def get_last_n_interactions(self, n=5):
        """Get last N interactions"""
        return list(self.history)[-n:]
    
    def get_session_duration(self):
        """Get how long this session has been running"""
        duration = datetime.now() - self.session_start
        return duration.total_seconds()
    
    def get_session_stats(self):
        """Get session statistics"""
        return {
            "commands_executed": self.command_count,
            "session_duration": self.get_session_duration(),
            "last_app": self.last_app_opened,
            "success_rate": self._calculate_success_rate()
        }
    
    def _calculate_success_rate(self):
        """Calculate success rate of commands"""
        if not self.history:
            return 0.0
        
        successful = sum(1 for interaction in self.history if interaction["success"])
        return (successful / len(self.history)) * 100
    
    def clear_history(self):
        """Clear interaction history (but keep session stats)"""
        self.history.clear()
