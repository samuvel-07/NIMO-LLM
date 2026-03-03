# intent_classifier.py
"""
Smart Intent Classification for JARVIS
Understands what the user wants, not just keywords
"""
import re
from difflib import SequenceMatcher

class IntentClassifier:
    def __init__(self):
        self.intents = {
            "open_app": {
                "patterns": ["open", "launch", "start", "run", "fire up"],
                "keywords": ["chrome", "notepad", "calculator", "spotify", "vscode", "word", "excel"]
            },
            "close_app": {
                "patterns": ["close", "quit", "exit", "kill", "terminate", "shut down"],
                "keywords": ["chrome", "notepad", "calculator", "app", "application"]
            },
            "close_all_apps": {
                "patterns": ["close all", "close everything", "kill all apps", "terminate all"],
                "keywords": []
            },
            "play_media": {
                "patterns": ["play", "play song", "play music", "listen to"],
                "keywords": ["song", "music", "video", "youtube"]
            },
            "time_query": {
                "patterns": ["time", "what time", "what's the time", "tell me the time", "current time"],
                "keywords": []
            },
            "search_query": {
                "patterns": ["who is", "what is", "tell me about", "search for", "look up", "find"],
                "keywords": ["wikipedia"]
            },
            "joke": {
                "patterns": ["joke", "tell me a joke", "make me laugh", "something funny"],
                "keywords": []
            },
            "system_shutdown": {
                "patterns": ["shutdown", "shut down", "power off", "turn off"],
                "keywords": ["computer", "system", "pc"]
            },
            "greeting": {
                "patterns": ["hello", "hi", "hey", "good morning", "good evening"],
                "keywords": []
            },
            "status_query": {
                "patterns": ["how are you", "what's up", "status"],
                "keywords": []
            },
            "conversational_query": {
                "patterns": ["explain", "tell me about", "what do you think", "how do", 
                            "why", "can you help", "could you", "should i", "would you",
                            "describe", "define", "teach me"],
                "keywords": ["explain", "think", "opinion", "help", "about", "why", "how"]
            }
        }
    
    def classify(self, command):
        """
        Classify user command into intent + extract entities
        Returns: {
            "intent": str,
            "confidence": float (0-10),
            "entities": dict,
            "original_command": str
        }
        """
        command = command.lower().strip()
        
        if not command:
            return {
                "intent": "unknown",
                "confidence": 0,
                "entities": {},
                "original_command": command
            }
        
        best_intent = None
        best_score = 0
        
        # Score each intent
        for intent_name, intent_data in self.intents.items():
            score = 0
            
            # Check patterns (main phrases)
            for pattern in intent_data["patterns"]:
                if pattern in command:
                    score += 3  # Strong match
                else:
                    # Fuzzy matching for typos/variations
                    similarity = SequenceMatcher(None, pattern, command).ratio()
                    if similarity > 0.75:
                        score += 2
                    elif similarity > 0.6:
                        score += 1
            
            # Check keywords (supporting words)
            for keyword in intent_data["keywords"]:
                if keyword in command:
                    score += 1
            
            if score > best_score:
                best_score = score
                best_intent = intent_name
        
        # Extract entities (app names, search terms, etc.)
        entities = self._extract_entities(command, best_intent)
        
        return {
            "intent": best_intent if best_intent else "unknown",
            "confidence": best_score,
            "entities": entities,
            "original_command": command
        }
    
    def _extract_entities(self, command, intent):
        """Extract relevant information from command"""
        entities = {}
        
        if intent == "open_app" or intent == "close_app":
            # Extract app name
            app_name = self._extract_app_name(command)
            if app_name:
                entities["app_name"] = app_name
        
        elif intent == "play_media":
            # Extract song/video name
            for pattern in ["play", "listen to", "play song", "play music"]:
                if pattern in command:
                    song = command.replace(pattern, "").strip()
                    if song:
                        entities["media_name"] = song
                    break
        
        elif intent == "search_query":
            # Extract search term
            for pattern in ["who is", "what is", "tell me about", "search for", "look up", "find"]:
                if pattern in command:
                    search_term = command.replace(pattern, "").strip()
                    if search_term:
                        entities["search_term"] = search_term
                    break
        
        return entities
    
    def _extract_app_name(self, command):
        """Extract application name from command"""
        # Known apps
        known_apps = ["chrome", "notepad", "calculator", "spotify", "vscode", 
                      "word", "excel", "powerpoint", "firefox", "edge"]
        
        for app in known_apps:
            if app in command:
                return app
        
        # Try to extract unknown app name (word after "open/close")
        words = command.split()
        for i, word in enumerate(words):
            if word in ["open", "close", "launch", "start", "quit", "exit"]:
                if i + 1 < len(words):
                    potential_app = words[i + 1]
                    # Remove common filler words
                    if potential_app not in ["the", "a", "an", "my"]:
                        return potential_app
        
        return None
