import asyncio
from brain.orchestrator import Orchestrator

async def main():
    print("Initializing Orchestrator...")
    orchestrator = Orchestrator(skill_registry=None)

    print("Testing input: 'open chrome'")
    decision = await orchestrator.handle_input("open chrome", {})
    
    print("\n--- DECISION OUTPUT ---")
    print(decision)
    print("-----------------------")
    
    # Test a dangerous one
    print("\nTesting input: 'shutdown system'")
    decision_dangerous = await orchestrator.handle_input("shutdown system", {})
    print(decision_dangerous)

if __name__ == "__main__":
    asyncio.run(main())
