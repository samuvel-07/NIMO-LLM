import asyncio
from .arbitration_engine import ArbitrationEngine # type: ignore
from .skill_registry import SkillRegistry # type: ignore
from .execution_manager import ExecutionManager # type: ignore
from .permission_manager import PermissionManager # type: ignore
from .event_logger import EventLogger # type: ignore
from .event_bus import EventBus # type: ignore
from .ws_publisher import WebSocketPublisher # type: ignore
from .confirmation_manager import ConfirmationManager # type: ignore
from .llm_handler import LLMHandler # type: ignore
from .intelligence_router import generate_response # type: ignore
from .memory.short_term_memory import ShortTermMemory # type: ignore
from .personality.jarvis_voice import JarvisVoice # type: ignore

try:
    from brain.utils.tts import speak  # type: ignore
except ImportError:
    def speak(text): print(f"[MOCK TTS] {text}")


class Orchestrator:

    def __init__(self):
        self.skill_registry = SkillRegistry()
        self.arbitration = ArbitrationEngine(self.skill_registry)
        self.executor = ExecutionManager(timeout=5)
        self.permission_manager = PermissionManager()
        self.confirmation_manager = ConfirmationManager(timeout_seconds=30)
        self.llm = LLMHandler()

        # v4.0 — Memory & Personality
        self.memory = ShortTermMemory()
        self.voice = JarvisVoice()

        # Event System
        self.bus = EventBus()
        self.logger = EventLogger()
        self.ws_publisher = WebSocketPublisher()

        # Subscribe
        self.bus.subscribe(self.logger.handle_event)
        self.bus.subscribe(self.ws_publisher.subscriber)

        self._lock = asyncio.Lock()

    async def start(self):
        """Start background services (WebSocket, etc)."""
        await self.ws_publisher.start_server()

    async def handle_input(self, text: str, context: dict):
        async with self._lock:
            return await self._process_input(text, context)

    async def _process_input(self, text: str, context: dict):
        # 1. Check for Pending Confirmation
        if self.confirmation_manager.is_pending(context):

            if self.confirmation_manager.is_expired(context):
                self.confirmation_manager.clear(context)
                await self.bus.emit("CONFIRMATION_EXPIRED", {})
                return "Confirmation expired."

            normalized = text.strip().lower()

            if normalized in ["yes", "confirm", "proceed", "sure", "ok", "do it"]:
                pending = self.confirmation_manager.get_pending(context)
                skill_name = pending["skill"]
                skill_instance = self.skill_registry.get_skill(skill_name)
                original_input = pending["payload"]

                self.confirmation_manager.clear(context)

                await self.bus.emit("CONFIRMATION_ACCEPTED", {
                    "skill": skill_name
                })

                if skill_instance:
                    await self.bus.emit("EXECUTION_START", {
                        "skill": skill_instance.name
                    })

                    execution_result = await self.executor.execute(
                        skill_instance, original_input, context
                    )

                    if execution_result.success:
                        entity = ShortTermMemory.extract_entity(original_input, skill_name)
                        self.memory.update(skill_name, entity)

                        # Minimal tactical speech
                        if self.voice.should_speak(skill_name, success=True):
                            response_text = self.voice.generate(skill_name, entity, success=True)
                            speak(response_text)

                        await self.bus.emit("EXECUTION_SUCCESS", {
                            "skill": skill_instance.name,
                            "duration": execution_result.duration,
                            "confidence": 1.0,
                            "source": "confirmed"
                        })
                        self.arbitration.context_scorer.update_memory(context, skill_name)
                        return execution_result.output
                    else:
                        error_response = self.voice.generate(skill_name, success=False)
                        speak(error_response)

                        await self.bus.emit("EXECUTION_FAILURE", {
                            "skill": skill_instance.name,
                            "error": execution_result.error,
                            "duration": execution_result.duration
                        })
                        return f"Skill failed: {execution_result.error}"
                else:
                    return f"Error: Pending skill '{skill_name}' not found."

            elif normalized in ["no", "cancel", "stop", "abort", "don't"]:
                self.confirmation_manager.clear(context)
                await self.bus.emit("CONFIRMATION_CANCELLED", {})
                return "Action cancelled."

            else:
                await self.bus.emit("CONFIRMATION_PENDING_BLOCKED", {})
                return "Please confirm or cancel the pending action."

        # 2. Normal Arbitration
        decision = self.arbitration.evaluate(text, context)

        # Log Decision
        await self.bus.emit("DECISION", {
            "input": text,
            "action": decision.action,
            "skill": decision.skill,
            "confidence": decision.confidence,
            "margin": decision.scores,
        })

        if decision.action == "EXECUTE_SKILL":
            skill_instance = self.skill_registry.get_skill(decision.skill)

            if skill_instance:
                # Permission Check
                allowed, confirm_needed, reason = self.permission_manager.is_allowed(
                    skill_instance, decision.confidence
                )

                if not allowed:
                    await self.bus.emit("PERMISSION_DENIED", {
                        "skill": decision.skill,
                        "confidence": decision.confidence,
                        "level": skill_instance.permission_level,
                        "reason": reason
                    })
                    return f"Permission denied: {reason}"

                if confirm_needed:
                    self.confirmation_manager.create_pending(
                        context, skill_instance.name, text
                    )
                    await self.bus.emit("CONFIRMATION_REQUIRED", {
                        "skill": decision.skill,
                        "confidence": decision.confidence,
                        "reason": reason
                    })
                    return f"Confirmation Required: {reason} (Skill: {decision.skill})"

                # Execution
                await self.bus.emit("EXECUTION_START", {
                    "skill": skill_instance.name
                })

                execution_result = await self.executor.execute(
                    skill_instance, text, context
                )

                if execution_result.success:
                    # v4.0 — Memory update
                    entity = ShortTermMemory.extract_entity(text, decision.skill)
                    self.memory.update(decision.skill, entity)

                    # v4.0 — Minimal tactical speech
                    if self.voice.should_speak(decision.skill, success=True):
                        # Vocal skills use execution output as entity
                        if decision.skill in ("time_query", "system_status", "status_report",
                                              "focus_mode", "stealth_mode", "strategic_mode"):
                            tts_entity = execution_result.output
                        else:
                            tts_entity = entity
                        response_text = self.voice.generate(decision.skill, tts_entity, success=True)
                        speak(response_text)
                    else:
                        print(f"[SILENT] {decision.skill} executed (no speech)")

                    await self.bus.emit("EXECUTION_SUCCESS", {
                        "skill": skill_instance.name,
                        "duration": execution_result.duration,
                        "confidence": decision.confidence,
                        "source": "deterministic"
                    })
                    self.arbitration.context_scorer.update_memory(context, decision.skill)
                    return execution_result.output
                else:
                    error_response = self.voice.generate(decision.skill, success=False)
                    speak(error_response)

                    await self.bus.emit("EXECUTION_FAILURE", {
                        "skill": skill_instance.name,
                        "error": execution_result.error,
                        "duration": execution_result.duration
                    })
                    return f"Skill failed: {execution_result.error}"
            else:
                error_msg = f"Skill '{decision.skill}' not found in registry."
                await self.bus.emit("REGISTRY_ERROR", {"message": error_msg})
                return error_msg

        elif decision.action == "CLARIFY":
            clarify_msg = self.voice.generate("clarify")
            speak(clarify_msg)
            return f"Ambiguous request. Did you mean: {decision.skill}? (Confidence: {decision.confidence:.2f})"

        elif decision.action == "LLM_FALLBACK":
            print(f"[LLM] Protocol: CONVERSATION_MODE (Confidence: {decision.confidence:.2f})")

            response = generate_response(text)

            if response:
                speak(response)
                await self.bus.emit("LLM_RESPONSE", {
                    "confidence": decision.confidence,
                    "source": "conversation_mode"
                })
                return response
            else:
                print("[ERROR] Intelligence failure — no response generated")
                return ""

        return decision
