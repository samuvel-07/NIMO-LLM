import asyncio
from .arbitration_engine import ArbitrationEngine
from .skill_registry import SkillRegistry
from .execution_manager import ExecutionManager
from .permission_manager import PermissionManager
from .event_logger import EventLogger
from .event_bus import EventBus
from .ws_publisher import WebSocketPublisher
from .confirmation_manager import ConfirmationManager

class Orchestrator:

    def __init__(self):
        self.skill_registry = SkillRegistry()
        self.arbitration = ArbitrationEngine(self.skill_registry)
        self.executor = ExecutionManager(timeout=5)
        self.permission_manager = PermissionManager()
        self.confirmation_manager = ConfirmationManager(timeout_seconds=30)
        
        # Event System
        self.bus = EventBus()
        self.logger = EventLogger()
        self.ws_publisher = WebSocketPublisher()
        
        # Subscribe
        self.bus.subscribe(self.logger.handle_event)
        self.bus.subscribe(self.ws_publisher.subscriber)
        
        self._lock = asyncio.Lock()

    async def start(self):
        """
        Start background services (WebSocket, etc).
        """
        await self.ws_publisher.start_server()

    async def handle_input(self, text: str, context: dict):
        async with self._lock:
            return await self._process_input(text, context)

    async def _process_input(self, text: str, context: dict):
        # 1. Check for Pending Confirmation
        if self.confirmation_manager.is_pending(context):
            
            # Check Expiry
            if self.confirmation_manager.is_expired(context):
                self.confirmation_manager.clear(context)
                await self.bus.emit("CONFIRMATION_EXPIRED", {})
                return "Confirmation expired."

            normalized = text.strip().lower()
            
            # Handle YES/CONFIRM
            if normalized in ["yes", "confirm", "proceed", "sure", "ok", "do it"]:
                pending = self.confirmation_manager.get_pending(context)
                skill_name = pending["skill"]
                # Payload was the original input text for the skill? 
                # Wait, 'payload' in create_pending call in user request was 'text'. 
                # So we use that as input to execute?
                # Yes, "payload": payload maps to skill execution input.
                
                skill_instance = self.skill_registry.get_skill(skill_name)
                original_input = pending["payload"]
                
                self.confirmation_manager.clear(context)
                
                await self.bus.emit("CONFIRMATION_ACCEPTED", {
                    "skill": skill_name
                })
                
                # Execute the originally requested skill
                # Note: We skip permission check here because we assume if it hit confirmation, 
                # it was already permission checked (and required confirmation).
                # But wait, execute() inside Orchestrator wasn't separated well. 
                # We should probably refactor or just call executor directly.
                
                # Logic: execute() needs skill instance.
                if skill_instance:
                     # Execution Start
                    await self.bus.emit("EXECUTION_START", {
                        "skill": skill_instance.name
                    })

                    execution_result = await self.executor.execute(
                        skill_instance, original_input, context
                    )
                    
                    if execution_result.success:
                        await self.bus.emit("EXECUTION_SUCCESS", {
                            "skill": skill_instance.name,
                            "duration": execution_result.duration
                        })
                        # Update memory
                        self.arbitration.context_scorer.update_memory(context, skill_name)
                        return execution_result.output
                    else:
                        await self.bus.emit("EXECUTION_FAILURE", {
                            "skill": skill_instance.name,
                            "error": execution_result.error,
                            "duration": execution_result.duration
                        })
                        return f"Skill failed: {execution_result.error}"
                else:
                    return f"Error: Pending skill '{skill_name}' not found."

            # Handle NO/CANCEL
            elif normalized in ["no", "cancel", "stop", "abort", "don't"]:
                self.confirmation_manager.clear(context)
                await self.bus.emit("CONFIRMATION_CANCELLED", {})
                return "Action cancelled."
            
            # Strict Lock Mode: Block unrelated input
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
                allowed, confirm_needed, reason = self.permission_manager.is_allowed(skill_instance, decision.confidence)
                
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
                        context,
                        skill_instance.name,
                        text
                    )
                    await self.bus.emit("CONFIRMATION_REQUIRED", {
                        "skill": decision.skill,
                        "confidence": decision.confidence,
                        "reason": reason
                    })
                    return f"Confirmation Required: {reason} (Skill: {decision.skill})"

                # Execution Start
                await self.bus.emit("EXECUTION_START", {
                    "skill": skill_instance.name
                })

                # Use safe execution manager
                execution_result = await self.executor.execute(
                    skill_instance, text, context
                )

                if execution_result.success:
                    await self.bus.emit("EXECUTION_SUCCESS", {
                        "skill": skill_instance.name,
                        "duration": execution_result.duration
                    })
                    # Only update memory on success
                    self.arbitration.context_scorer.update_memory(context, decision.skill)
                    return execution_result.output
                else:
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

        return decision
