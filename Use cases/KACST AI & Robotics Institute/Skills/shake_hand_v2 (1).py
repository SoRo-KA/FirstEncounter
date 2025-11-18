import asyncio
from pymirokai.robot import Robot
from pymirokai.decorators.skill import skill
from pymirokai.enums.enums import AccessLevel, Hand, Arm


@skill(
    access_level=AccessLevel.USER,
    verbal_descriptions={
        "en": ["shake hand", "shake my hand", "shake"],
    },
)
async def shake_hand(robot: Robot) -> dict:
    """Welcome the user and perform a handshake gesture."""

    # Speak welcome sentence
    message = "Hi, I'm Miroka, nice to meet you!, lets shake my hand"
    await robot.say(message).started()

    await robot.give_hand().completed()

    # Let the robot roam for 7 seconds
    await asyncio.sleep(3)

    # Step 3: Bring both arms down
    await robot.arms_down().completed()

    
