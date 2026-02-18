import asyncio
import time

class ExecutionResult:
    def __init__(self, success, output=None, error=None, duration=None):
        self.success = success
        self.output = output
        self.error = error
        self.duration = duration


class ExecutionManager:

    def __init__(self, timeout=5):
        self.timeout = timeout

    async def execute(self, skill, text, context):
        """
        Executes a skill safely with timeout and error handling.
        """
        start_time = time.time()

        try:
            # skills are async
            result = await asyncio.wait_for(
                skill.execute(text, context),
                timeout=self.timeout
            )

            duration = time.time() - start_time

            return ExecutionResult(
                success=True,
                output=result,
                duration=duration
            )

        except asyncio.TimeoutError:
            return ExecutionResult(
                success=False,
                error=f"Execution Timeout ({self.timeout}s)",
                duration=time.time() - start_time
            )

        except Exception as e:
            # Catch-all for skill crashes
            return ExecutionResult(
                success=False,
                error=f"Runtime Error: {str(e)}",
                duration=time.time() - start_time
            )
