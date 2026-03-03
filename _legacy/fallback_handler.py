# fallback_handler.py
"""
Smart Fallback Handler for JARVIS
Intelligently handles confusion and provides helpful guidance
"""

class FallbackHandler:
    def __init__(self, context_manager, response_generator):
        self.context = context_manager
        self.response_gen = response_generator
        self.confusion_count = 0
        self.last_clarification = None
    
    def handle_unclear_command(self, command, classified_intent):
        """
        Handle commands with low confidence or unclear intent
        
        Returns:
            - None if command is clear enough to proceed
            - String response if clarification is needed
        """
        confidence = classified_intent["confidence"]
        intent = classified_intent["intent"]
        entities = classified_intent.get("entities", {})
        
        # Very low confidence - didn't understand at all
        if confidence < 1 or intent == "unknown":
            self.confusion_count += 1
            
            # After 2 misunderstandings, offer help menu
            if self.confusion_count >= 2:
                return self._offer_help()
            
            # Try to suggest based on context
            suggestion = self._suggest_based_on_context(command)
            if suggestion:
                return f"Did you mean: {suggestion}?"
            
            return self.response_gen.generate("not_understood")
        
        # Medium confidence - understood intent but missing details
        if confidence < 3:
            # Check if we're missing critical entities
            if self._missing_critical_entity(intent, entities):
                return self.response_gen.get_clarification(intent, entities)
        
        # Low confidence but has required info - confirm before executing sensitive actions
        if confidence < 4 and self._is_sensitive_action(intent):
            return self.response_gen.get_confirmation(intent, **entities)
        
        # Command is clear enough, reset confusion counter
        self.confusion_count = 0
        return None
    
    def _missing_critical_entity(self, intent, entities):
        """Check if command is missing required information"""
        
        # These intents require specific entities
        required_entities = {
            "open_app": "app_name",
            "close_app": "app_name",
            "play_media": "media_name",
            "search_query": "search_term"
        }
        
        if intent in required_entities:
            required_field = required_entities[intent]
            return required_field not in entities or not entities[required_field]
        
        return False
    
    def _is_sensitive_action(self, intent):
        """Check if this is a sensitive action requiring confirmation"""
        sensitive_actions = [
            "system_shutdown",
            "close_all_apps"
        ]
        return intent in sensitive_actions
    
    def _suggest_based_on_context(self, command):
        """
        Try to guess what user meant based on conversation history
        """
        last = self.context.get_last_interaction()
        if not last:
            return None
        
        command_lower = command.lower()
        
        # If they just opened something and command has "close"
        if last["intent"] == "open_app" and "close" in command_lower:
            app = last.get("entities", {}).get("app_name")
            if app:
                return f"close {app}"
        
        # If they just closed something and command has "open"
        if last["intent"] == "close_app" and "open" in command_lower:
            app = last.get("entities", {}).get("app_name")
            if app:
                return f"open {app}"
        
        # If they just played something and command has "play"
        if last["intent"] == "play_media" and "play" in command_lower:
            media = last.get("entities", {}).get("media_name")
            if media:
                return f"play {media}"
        
        return None
    
    def _offer_help(self):
        """
        Provide help menu when user is repeatedly confused
        """
        help_text = (
            "I can help with: "
            "open apps, close apps, play music, "
            "check time, search Wikipedia, tell jokes, "
            "or shut down your system. What would you like?"
        )
        
        # Reset confusion after showing help
        self.confusion_count = 0
        
        return help_text
    
    def handle_partial_match(self, intent, entities, apps_list):
        """
        Handle when app name is partially matched
        
        Args:
            intent: The intent (open_app, close_app)
            entities: Extracted entities
            apps_list: List of available apps
        
        Returns:
            Suggestion string or None
        """
        if "app_name" not in entities:
            return None
        
        requested_app = entities["app_name"].lower()
        
        # Find closest matches in available apps
        close_matches = []
        for app in apps_list:
            if requested_app in app.lower() or app.lower() in requested_app:
                close_matches.append(app)
        
        if len(close_matches) == 1:
            return f"Did you mean {close_matches[0]}?"
        elif len(close_matches) > 1:
            apps = ", ".join(close_matches[:3])
            return f"Did you mean one of these: {apps}?"
        
        return None
    
    def reset_confusion(self):
        """Reset confusion counter (call after successful command)"""
        self.confusion_count = 0
