import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from brain.orchestrator import Orchestrator

async def test():
    print("Initializing Orchestrator...")
    orchestrator = Orchestrator()
    
    # Force reload of skills effectively by just running. 
    # (Registry loads on init).
    
    print("\n--- Test 1: Timeout Safety ---")
    # "timeout" -> TimeoutSkill -> sleep(6) -> TimeoutError (5s limit)
    result = await orchestrator.handle_input("run timeout test", {})
    print(f"Result: {result}")
    
    if "Execution Timeout" in str(result):
        print("SUCCESS: Timeout caught.")
    else:
        print("FAILURE: Timeout did not trigger.")

    print("\n--- Test 2: Crash Safety ---")
    # "crash" -> TimeoutSkill -> raises ValueError
    result = await orchestrator.handle_input("run crash test", {})
    print(f"Result: {result}")
    
    if "Runtime Error" in str(result) and "Intentional Crash" in str(result):
        print("SUCCESS: Crash caught.")
    else:
        print("FAILURE: Crash not caught.")

if __name__ == "__main__":
    asyncio.run(test())
