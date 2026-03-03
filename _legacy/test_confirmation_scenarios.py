import asyncio
import sys
import os
import time

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from brain.orchestrator import Orchestrator

async def test():
    print("Initializing Orchestrator for Scenario Tests...")
    orchestrator = Orchestrator()
    await orchestrator.start()
    
    # helper
    async def run_input(text, context, label="Input"):
        print(f"\n--- {label}: '{text}' ---")
        res = await orchestrator.handle_input(text, context)
        print(f"Result: {res}")
        return res

    # Scenario 1: destroy system -> yes
    print("\n=== Scenario 1: destroy system -> yes ===")
    ctx1 = {}
    await run_input("destroy system", ctx1)
    await run_input("yes", ctx1)
    
    # Scenario 2: destroy system -> no
    print("\n=== Scenario 2: destroy system -> no ===")
    ctx2 = {}
    await run_input("destroy system", ctx2)
    await run_input("no", ctx2)

    # Scenario 3: destroy system -> wait -> yes
    print("\n=== Scenario 3: destroy system -> wait -> yes ===")
    ctx3 = {}
    # Temporarily shorten timeout for test
    orchestrator.confirmation_manager.timeout = 2
    
    await run_input("destroy system", ctx3)
    print("...waiting 2.5 seconds for expiry...")
    time.sleep(2.5)
    await run_input("yes", ctx3, label="Input (after timeout)")
    
    # Restore timeout
    orchestrator.confirmation_manager.timeout = 30
    
    # Scenario 4: destroy system -> open chrome (Strict Mode: Should be BLOCKED)
    print("\n=== Scenario 4: destroy system -> open chrome (Strict Mode) ===")
    ctx4 = {} 
    
    # 4a. Trigger confirmation
    await run_input("destroy system", ctx4)
    
    # 4b. Send unrelated command
    res = await run_input("open chrome", ctx4)
    if "Please confirm or cancel" in str(res):
        print("PASS: Unrelated input blocked.")
    else:
        print(f"FAIL: Input was not blocked. Result: {res}")
    
    # 4c. Verify pending is still there
    is_pending = orchestrator.confirmation_manager.is_pending(ctx4)
    print(f"Pending Confirmation Active: {is_pending}")


if __name__ == "__main__":
    asyncio.run(test())
