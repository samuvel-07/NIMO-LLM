import asyncio
import sys
import os
import time

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from brain.orchestrator import Orchestrator

# Mock time to control decay
original_time = time.time
mock_time = 0.0

def get_mock_time():
    return mock_time

async def test():
    global mock_time
    # Initialize Orchestrator
    orchestrator = Orchestrator()
    # Patch time in context_scorer (Monkey Patching for test)
    orchestrator.arbitration.context_scorer.__class__.__module__
    # Actually, simpler to just patch time.time globally if possible, but python imports might bind early.
    # Let's just modify the context manually for the test since logic relies on timestamps in context.
    
    print("Initializing Orchestrator...")
    
    # 1. Execute 'open chrome' to seed memory
    print("\n--- Step 1: Execute 'open chrome' (Seed Memory) ---")
    context = {}
    
    # We need to successfully execute. 'open chrome' should execute open_app.
    result = await orchestrator.handle_input("open chrome", context)
    
    if hasattr(result, "action"):
         print(f"Decision: {result.action} ({result.skill})")
    else:
         print(f"Decision: EXECUTED (Output: {result})")
    
    if "skill_memory" in context and "open_app" in context["skill_memory"]:
        weight = context["skill_memory"]["open_app"]["weight"]
        print(f"Memory Weight: {weight:.3f}")
        if 0.14 <= weight <= 0.16:
             print("SUCCESS: Memory seeded.")
        else:
             print("FAILURE: Memory not seeded correctly.")
    else:
        print("FAILURE: No memory created.")
        return

    # 2. fast forward time by modifying the timestamp in context
    # Decay lambda is 0.5. 
    # Exp(-0.5 * minutes). 
    # Let's say 2 minutes pass. Exp(-1) ~= 0.368.
    # New weight should be 0.15 * 0.368 ~= 0.055.
    
    print("\n--- Step 2: Simulate 2 Minutes Passing ---")
    # Manually backdate the timestamp
    context["skill_memory"]["open_app"]["last_updated"] -= (2 * 60)
    
    # Now query for "open" (ambiguous). 
    # Without memory: 0.50 (Normalized) / 0.18 (Raw)
    # With decayed memory: Boost is small.
    # Raw 'open_app' score matches 'open' -> 0.3 (or 0.3 * something)
    # Let's see the score from context_scorer directly first
    
    context_scores = orchestrator.arbitration.context_scorer.score("any", context)
    decayed_boost = context_scores.get("open_app", 0.0)
    print(f"Decayed Boost (calculated): {decayed_boost:.3f}")
    
    if 0.05 <= decayed_boost <= 0.06:
        print("SUCCESS: Decay calculation correct (approx 0.055).")
    else:
        print(f"FAILURE: Decay calculation off. Expected ~0.055, got {decayed_boost:.3f}")

if __name__ == "__main__":
    asyncio.run(test())
