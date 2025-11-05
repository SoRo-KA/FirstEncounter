"""
Simple serving visitor skill.
"""

import asyncio
from pymirokai.decorators.skill import skill
from pymirokai.enums.enums import AccessLevel
from pymirokai.robot import Robot

@skill(
    access_level=AccessLevel.USER,
    verbal_descriptions={
        "en": [
            "serve visitor",
            "serve basket"
        ]
    },
)
async def serve_visitor(robot: Robot) -> dict:
    """
    Makes the robot say a simple welcoming and serving phrase.
    
    Args:
        robot: The Robot instance
    
    Returns:
        dict: Result information
    """
    # Say welcoming phrase
    await say_and_wait(robot, "Welcome! It's a pleasure to serve you today.")
    
    # Brief pause
    await asyncio.sleep(1)
    
    # Say more polite serving phrase
    await say_and_wait(robot, "I would be honored if you would select something from this basket. Please take your time.")
    
    return {"llm_output": "Robot greeted and served visitor"}

async def say_and_wait(robot: Robot, message: str):
    """Have the robot say a message and wait until it's done."""
    print(f"DEBUG: {message}")  # Print to console for debugging
    mission = robot.say(message)
    await mission.started()
    await asyncio.sleep(0.5)
