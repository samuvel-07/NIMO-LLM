import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from brain.orchestrator import Orchestrator

async def test():
    print("Initializing Orchestrator for Telemetry Test...")
    orchestrator = Orchestrator()
    await orchestrator.start()
    
    commands = [
        "open chrome",   # Should be EXECUTE_SKILL -> SUCCESS
        "open",          # Should be CLARIFY
        "destroy system" # Should be EXECUTE_SKILL -> CONFIRMATION_REQUIRED
    ]

    print(f"\nRunning commands: {commands}\n")

    for text in commands:
        print(f"--- Input: '{text}' ---")
        result = await orchestrator.handle_input(text, {})
        print(f"Result: {result}\n")

if __name__ == "__main__":
    asyncio.run(test())
