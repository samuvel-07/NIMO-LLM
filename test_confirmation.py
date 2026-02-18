import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from brain.orchestrator import Orchestrator

async def test():
    print("Initializing Orchestrator for Confirmation Test...")
    orchestrator = Orchestrator()
    await orchestrator.start()
    
    context = {}

    print("\n--- Step 1: Request Critical Skill (destroy system) ---")
    res1 = await orchestrator.handle_input("destroy system", context)
    print(f"Result 1: {res1}")
    
    # Check if pending
    is_pending = orchestrator.confirmation_manager.is_pending(context)
    print(f"Pending Confirmation: {is_pending}")
    
    if not is_pending:
        print("FAIL: Should be pending confirmation.")
        return

    print("\n--- Step 2: Confirm Action (yes) ---")
    res2 = await orchestrator.handle_input("yes", context)
    print(f"Result 2: {res2}")
    
    # Check if no longer pending
    is_pending_after = orchestrator.confirmation_manager.is_pending(context)
    print(f"Pending Confirmation After: {is_pending_after}")
    
    if is_pending_after:
        print("FAIL: Should not be pending after confirmation.")
    
    print("\n--- Step 3: Request Critical Skill Again ---")
    await orchestrator.handle_input("destroy system", context)
    
    print("\n--- Step 4: Cancel Action (no) ---")
    res3 = await orchestrator.handle_input("no", context)
    print(f"Result 3: {res3}")
    
    print("\n--- Step 5: Unrelated Input while Pending ---")
    await orchestrator.handle_input("destroy system", context)
    print("(Pending set again)")
    
    res4 = await orchestrator.handle_input("open chrome", context)
    print(f"Result 4 (Unrelated): {res4}")
    
    # Pendng should still be true?
    # User requirement: "If user says unrelated input: → Treat normally, pending remains."
    is_pending_still = orchestrator.confirmation_manager.is_pending(context)
    print(f"Pending Still Active: {is_pending_still}")

if __name__ == "__main__":
    asyncio.run(test())
