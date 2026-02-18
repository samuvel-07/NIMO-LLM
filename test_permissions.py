import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from brain.orchestrator import Orchestrator

async def test():
    print("Initializing Orchestrator...")
    orchestrator = Orchestrator()
    
    # 1. Test LOW permission (normal)
    print("\n--- Test 1: LOW Permission (Open Chrome) ---")
    # 'open chrome' -> 1.0 confidence -> > 0.80 -> Pass
    res1 = await orchestrator.handle_input("open chrome", {})
    print(f"Result: {res1}")
    if "Pretending" in str(res1):
        print("SUCCESS: LOW permission passed.")
    else:
        print("FAILURE: LOW permission blocked or failed.")

    # 2. Test CRITICAL permission (Critical Skill)
    print("\n--- Test 2: CRITICAL Permission (Destroy System) ---")
    # We need to simulate a case where confidence is high enough to execute (>0.80) 
    # but lower than critical threshold (0.92).
    # But wait, our 'critical_skill' has 1.0 keywords.
    # KeywordScorer sums weights. 'destroy system' -> 2.0 -> capped at 1.0.
    # So it will be 1.0. 1.0 >= 0.92. 
    # BUT now it requires CONFIRMATION.
    
    res2 = await orchestrator.handle_input("destroy system", {})
    print(f"Result: {res2}")
    if "Confirmation Required" in str(res2):
        print("SUCCESS: CRITICAL permission correctly requested confirmation.")
    elif "Critical Action Executed" in str(res2):
        print("FAILURE: CRITICAL permission executed without confirmation!")

    # 3. Test CRITICAL permission denial
    # We need to artificially lower the confidence.
    # Or make a query that matches weakly.
    # 'destroy' -> 1.0 keyword score.
    # But let's say we have 'destroy something else'
    # 'destroy' (1.0). Norm score might be 1.0 if no competition.
    # To test refusal, we need confidence < 0.92 but > .80.
    # How to achieve that with current scoring?
    # If we have competition?
    # Or manually tweak for test.
    # Actually, we can just monkey-patch the tier threshold for testing.
    
    print("\n--- Test 3: CRITICAL Permission Denial ---")
    # Temporarily raise CRITICAL threshold to 1.1 (impossible)
    orchestrator.permission_manager.tier_thresholds["CRITICAL"] = 1.1
    
    res3 = await orchestrator.handle_input("destroy system", {})
    print(f"Result: {res3}")
    
    if "Permission denied" in str(res3):
        print("SUCCESS: CRITICAL permission denied when threshold not met.")
    else:
        print("FAILURE: Should have been denied.")

if __name__ == "__main__":
    asyncio.run(test())
