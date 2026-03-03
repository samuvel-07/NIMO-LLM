
import sys
import os
import asyncio

# Setup path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from brain.utils.tts import speak # type: ignore
from skills.open_app import OpenAppSkill # type: ignore

async def test():
    print("Testing TTS...")
    speak("Testing text to speech system.")
    
    print("Testing App Launch (Calculator)...")
    skill = OpenAppSkill()
    result = await skill.execute("open calculator", {})
    print(f"Result: {result}")
    
    speak(result)

if __name__ == "__main__":
    asyncio.run(test())
