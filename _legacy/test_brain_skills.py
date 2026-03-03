import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from brain.orchestrator import Orchestrator

async def test():
    print("Initializing Orchestrator...")
    orchestrator = Orchestrator()
    
    print("\nTest 1: 'open chrome'")
    decision = await orchestrator.handle_input("open chrome", {})
    print(f"Decision: {decision}")

    if decision.action == "EXECUTE_SKILL" and decision.skill == "open_app":
        print("SUCCESS: Correctly identified 'open_app' skill.")
    else:
        print(f"FAILURE: Expected 'EXECUTE_SKILL' for 'open_app', got {decision.action} for {decision.skill}")
        print(f"Scores: {decision.scores}")

if __name__ == "__main__":
    asyncio.run(test())
