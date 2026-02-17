# jarvis_core.py (UPGRADED with Intent, Context, Natural Responses, and Fallback)
import os, time, subprocess, datetime, json
import pyttsx3, pywhatkit, wikipedia, pyjokes
from vosk import Model, KaldiRecognizer
import pyaudio, sounddevice as sd, wavio
import whisper
import threading

# Import the new smart modules
from intent_classifier import IntentClassifier
from context_manager import ContextManager
from response_generator import ResponseGenerator
from fallback_handler import FallbackHandler
from llm_handler import LLMHandler

# Path to Vosk model folder
VOSK_MODEL_PATH = os.path.join(os.path.dirname(__file__), "vosk-model-small-en-in-0.4")
if not os.path.isdir(VOSK_MODEL_PATH):
    raise FileNotFoundError(f"Vosk model folder not found at {VOSK_MODEL_PATH}. Download and unzip model there.")

vosk_model = Model(VOSK_MODEL_PATH)
TTS_RATE = 165

def _init_tts():
    engine = pyttsx3.init()
    engine.setProperty("rate", TTS_RATE)
    return engine

def _speak_text(engine, text, log_fn):
    log_fn("JARVIS: " + text)
    try:
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        log_fn("TTS error: " + str(e))

def _listen_with_vosk(timeout_secs=3):
    """Low-latency streaming recognition"""
    rec = KaldiRecognizer(vosk_model, 16000)
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=4096)
    stream.start_stream()
    text = ""
    frames = int(timeout_secs * (16000 / 4096)) + 1
    import json as _json
    try:
        for _ in range(frames):
            data = stream.read(4096, exception_on_overflow=False)
            if rec.AcceptWaveform(data):
                res = _json.loads(rec.Result())
                text = res.get("text", "").lower()
                break
    except Exception:
        text = ""
    finally:
        try:
            stream.stop_stream()
            stream.close()
            p.terminate()
        except Exception:
            pass
    return text

def _record_for_whisper(seconds=5, filename=None):
    """Record audio for Whisper fallback"""
    fs = 16000
    if filename is None:
        filename = os.path.join(os.path.dirname(__file__), "tmp_whisper.wav")
    audio = sd.rec(int(seconds * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()
    wavio.write(filename, audio, fs, sampwidth=2)
    return filename

class JarvisCore(threading.Thread):
    def __init__(self, log_fn=print):
        super().__init__(daemon=True)
        self.log = log_fn
        self.running = False
        self.engine = _init_tts()
        self._whisper_model = None
        self.wake = "jarvis"
        
        # Load apps & memory
        self.memory_path = os.path.join(os.path.dirname(__file__), "memory.json")
        self.apps_path = os.path.join(os.path.dirname(__file__), "apps.json")
        self.memory = self._load_json(self.memory_path)
        self.apps = self._load_json(self.apps_path)
        
        # Initialize smart modules
        self.intent_classifier = IntentClassifier()
        self.context_manager = ContextManager()
        self.response_generator = ResponseGenerator()
        self.fallback_handler = FallbackHandler(
            self.context_manager,
            self.response_generator
        )
        
        # Initialize LLM handler
        self.llm_handler = LLMHandler(log_fn=self.log)
        
        if self.llm_handler.is_available():
            self.log("Smart modules loaded: Intent, Context, Response, Fallback, LLM")
        else:
            self.log("Smart modules loaded: Intent, Context, Response, Fallback (LLM unavailable)")

    def _load_json(self, p):
        try:
            return json.load(open(p, "r", encoding="utf-8"))
        except Exception:
            return {}

    def _save_json(self, p, data):
        json.dump(data, open(p, "w", encoding="utf-8"), indent=2)

    def speak(self, text):
        _speak_text(self.engine, text, self.log)

    def run(self):
        self.running = True
        self.speak("Jarvis online. Smart mode enabled.")
        
        while self.running:
            # Vosk quick listen
            try:
                partial = _listen_with_vosk(timeout_secs=3)
            except Exception as e:
                self.log("Vosk listen error: " + str(e))
                partial = ""
            
            if not partial:
                # Fallback to Whisper
                try:
                    fname = _record_for_whisper(4)
                    if self._whisper_model is None:
                        self._whisper_model = whisper.load_model("base")
                    res = self._whisper_model.transcribe(fname)
                    partial = (res.get("text") or "").lower()
                except Exception as e:
                    self.log("Whisper error: " + str(e))
                    partial = ""
            
            if not partial:
                continue
            
            self.log("Heard: " + partial)
            
            # Check for wake word
            if self.wake in partial:
                # Extract command (remove wake word)
                cmd = partial.replace(self.wake, "").strip()
                
                if not cmd:
                    # Just wake word, no command
                    response = self.response_generator.generate("wake_acknowledged")
                    self.speak(response)
                    continue
                
                self.log("Command: " + cmd)
                
                # Process with smart system
                self.process_command(cmd)
        
        self.speak("Jarvis stopped.")

    def stop(self):
        self.running = False

    def process_command(self, raw_command):
        """
        Smart command processing pipeline:
        1. Resolve context references ("it", "again")
        2. Classify intent
        3. Check if clarification needed
        4. Execute command
        5. Generate natural response
        6. Store in context
        """
        
        # Step 1: Resolve references using context
        command = self.context_manager.resolve_reference(raw_command)
        if command != raw_command:
            self.log(f"Resolved: {raw_command} → {command}")
        
        # Step 2: Classify intent
        classified = self.intent_classifier.classify(command)
        self.log(f"Intent: {classified['intent']} (confidence: {classified['confidence']})")
        
        # Step 3: Check if clarification needed
        fallback_response = self.fallback_handler.handle_unclear_command(
            command, classified
        )
        
        if fallback_response:
            # Need clarification or confirmation
            self.speak(fallback_response)
            self.context_manager.add_interaction(
                raw_command, classified, fallback_response, success=False
            )
            return
        
        # Step 4: Execute the command
        success, result_msg = self._execute_intent(classified)
        
        # Step 5: Generate natural response
        if result_msg:
            # Custom result message from execution
            response = result_msg
        else:
            # Generate natural response
            response = self.response_generator.generate(
                classified["intent"],
                success=success,
                **classified.get("entities", {})
            )
        
        # Step 6: Store in context
        self.context_manager.add_interaction(
            command, classified, response, success
        )
        
        # Speak the response
        self.speak(response)
        
        # Reset confusion counter on success
        if success:
            self.fallback_handler.reset_confusion()

    def _execute_intent(self, classified):
        """
        Execute classified intent
        Returns: (success: bool, custom_message: str or None)
        """
        intent = classified["intent"]
        entities = classified.get("entities", {})
        
        try:
            # Route to appropriate handler
            if intent == "open_app":
                return self._handle_open_app(entities)
            
            elif intent == "close_app":
                return self._handle_close_app(entities)
            
            elif intent == "close_all_apps":
                return self._handle_close_all()
            
            elif intent == "play_media":
                return self._handle_play_media(entities)
            
            elif intent == "time_query":
                return self._handle_time_query()
            
            elif intent == "search_query":
                return self._handle_search(entities)
            
            elif intent == "joke":
                return self._handle_joke()
            
            elif intent == "system_shutdown":
                return self._handle_shutdown()
            
            elif intent == "greeting":
                return True, self.response_generator.generate("greeting")
            
            elif intent == "status_query":
                return self._handle_status_query()
            
            elif intent == "conversational_query":
                return self._handle_llm_conversation(classified)
            
            elif intent == "unknown":
                # For unknown intents with enough words, try LLM
                if len(classified["original_command"].split()) >= 4:
                    return self._handle_llm_conversation(classified)
                else:
                    return False, "I'm not sure how to handle that yet"
            
            else:
                return False, "I'm not sure how to handle that yet"
        
        except Exception as e:
            self.log(f"Execution error: {e}")
            return False, None

    def _handle_open_app(self, entities):
        """Handle opening applications"""
        app_name = entities.get("app_name")
        if not app_name:
            return False, "Which app should I open?"
        
        # Check if app is in registry
        app_path = self.apps.get(app_name)
        
        if app_path:
            try:
                os.startfile(app_path)
                return True, None
            except Exception as e:
                self.log(f"Failed to open {app_name}: {e}")
                return False, f"Failed to open {app_name}"
        else:
            # Try as raw exe name
            try:
                os.startfile(app_name)
                return True, None
            except Exception:
                # Suggest adding to registry
                return False, f"Can't find {app_name}. Add it via the GUI"

    def _handle_close_app(self, entities):
        """Handle closing applications"""
        app_name = entities.get("app_name")
        if not app_name:
            return False, "Which app should I close?"
        
        try:
            # Convert app name to process name
            process_name = app_name if app_name.endswith(".exe") else f"{app_name}.exe"
            os.system(f"taskkill /f /im {process_name} >nul 2>&1")
            return True, None
        except Exception as e:
            self.log(f"Failed to close {app_name}: {e}")
            return False, None

    def _handle_close_all(self):
        """Close all non-essential applications"""
        PROTECTED = ["explorer.exe", "svchost.exe", "System", "python.exe", "pythonw.exe"]
        try:
            out = subprocess.check_output("tasklist", shell=True).decode()
            closed_count = 0
            for line in out.splitlines()[3:]:
                if line.strip():
                    app = line.split()[0]
                    if app not in PROTECTED:
                        os.system(f"taskkill /f /im {app} >nul 2>&1")
                        closed_count += 1
            return True, f"Closed {closed_count} applications"
        except Exception as e:
            self.log(f"Close all error: {e}")
            return False, None

    def _handle_play_media(self, entities):
        """Handle playing media on YouTube"""
        media_name = entities.get("media_name")
        if not media_name:
            return False, "What should I play?"
        
        try:
            pywhatkit.playonyt(media_name)
            return True, None
        except Exception as e:
            self.log(f"Play media error: {e}")
            return False, f"Couldn't play {media_name}"

    def _handle_time_query(self):
        """Handle time queries"""
        now = datetime.datetime.now().strftime("%I:%M %p")
        return True, f"The time is {now}"

    def _handle_search(self, entities):
        """Handle Wikipedia searches"""
        search_term = entities.get("search_term")
        if not search_term:
            return False, "What should I search for?"
        
        try:
            info = wikipedia.summary(search_term, sentences=2)
            return True, info
        except wikipedia.exceptions.DisambiguationError as e:
            return True, f"Multiple results found. Try being more specific: {', '.join(e.options[:3])}"
        except wikipedia.exceptions.PageError:
            return False, f"Couldn't find anything about {search_term}"
        except Exception as e:
            self.log(f"Search error: {e}")
            return False, "Search failed"

    def _handle_joke(self):
        """Tell a joke"""
        try:
            joke = pyjokes.get_joke()
            return True, joke
        except Exception:
            return True, "Why did the developer go broke? Because he used up all his cache!"

    def _handle_shutdown(self):
        """Handle system shutdown"""
        delay = 10
        os.system(f"shutdown /s /t {delay}")
        return True, f"Shutting down in {delay} seconds. Save your work"

    def _handle_status_query(self):
        """Handle status queries"""
        stats = self.context_manager.get_session_stats()
        duration_mins = int(stats["session_duration"] / 60)
        
        status = (
            f"All systems operational. "
            f"I've executed {stats['commands_executed']} commands "
            f"in the last {duration_mins} minutes"
        )
        return True, status
    
    def _handle_llm_conversation(self, classified):
        """
        Handle open-ended conversations using LLM
        
        Args:
            classified: Classified intent data
        
        Returns:
            tuple: (success, response_message)
        """
        if not self.llm_handler.is_available():
            return False, "I can't answer that right now. Ollama LLM needs to be installed and running."
        
        user_query = classified["original_command"]
        
        try:
            # Generate LLM response
            response = self.llm_handler.generate_response(user_query, use_history=True)
            
            # Add to LLM conversation history
            self.llm_handler.add_to_history(user_query, response)
            
            return True, response
            
        except Exception as e:
            self.log(f"LLM conversation error: {e}")
            return False, "I'm having trouble with that question right now"

