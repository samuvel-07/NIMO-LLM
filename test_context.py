import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from brain.orchestrator import Orchestrator

async def test():
    print("Initializing Orchestrator...")
    orchestrator = Orchestrator()
    
    # Test 1: Ambiguous input "open" with NO context
    print("\n--- Test 1: 'open' (No Context) ---")
    decision_no_context = await orchestrator.handle_input("open", {})
    score_no_ctx = decision_no_context.scores.get("open_file", 0.0)
    print(f"Score for 'open_file': {score_no_ctx:.3f}")

    # Test 2: Ambiguous input "open" WITH context "open_file"
    print("\n--- Test 2: 'open' (Context: last_skill='open_file') ---")
    decision_with_context = await orchestrator.handle_input("open", {"last_skill": "open_file"})
    score_with_ctx = decision_with_context.scores.get("open_file", 0.0)
    print(f"Score for 'open_file': {score_with_ctx:.3f}")

    # Verification
    # With Max Normalization, the top skill is always 1.0.
    # We must check if the context created a MARGIN against the runner-up.
    
    # No Context: 'open_app' (0.18) vs 'open_file' (0.18). Normalizes to 1.0 vs 1.0. Margin 0.
    # With Context: 'open_app' (0.18) vs 'open_file' (0.207). 
    # Normalizes to: 'open_file' 1.0 vs 'open_app' (0.18/0.207 = ~0.87).
    # Margin should be ~0.13.
    
    scores_no_ctx = decision_no_context.scores
    scores_with_ctx = decision_with_context.scores
    
    # Get margins
    def get_margin(decision):
        sorted_s = sorted(decision.scores.values(), reverse=True)
        if len(sorted_s) > 1:
            return sorted_s[0] - sorted_s[1]
        return 0.0

    margin_no_ctx = get_margin(decision_no_context)
    margin_with_ctx = get_margin(decision_with_context)

    print(f"\nMargin (No Context): {margin_no_ctx:.3f}")
    print(f"Margin (With Context): {margin_with_ctx:.3f}")
    print(f"Action (No Context): {decision_no_context.action}")
    print(f"Action (With Context): {decision_with_context.action}")

    if margin_with_ctx > 0.10 and decision_with_context.action == "EXECUTE_SKILL":
        print("SUCCESS: Context boost created sufficient margin for execution.")
    else:
        print("FAILURE: Context did not create sufficient margin.")

if __name__ == "__main__":
    asyncio.run(test())
