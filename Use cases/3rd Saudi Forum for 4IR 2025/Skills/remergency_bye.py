import random
import asyncio
from pymirokai.decorators.skill import skill
from pymirokai.enums.enums import AccessLevel, Arm
from pymirokai.robot import Robot


@skill(
    access_level=AccessLevel.USER,
    verbal_descriptions={
        "en": [
            "goodbye", "bye", "see you", "see you later", "see you soon",
            "take care", "farewell", "bye bye", "catch you later",
        ],
        "fr": ["au revoir", "à bientôt", "salut", "à plus tard"],
    },
)
async def farewell(robot: Robot) -> None:
    """Robot says goodbye and waves."""
    farewells = [
        "Goodbye! It was great talking to you.",
        "See you soon! Have a wonderful day.",
        "Bye for now! Hope to see you again soon.",
        "Take care! It was nice meeting you.",
        "Goodbye! I hope you enjoyed our time together.",
        "See you later! Stay curious and inspired.",
        "Bye bye! I’ll be right here if you need me again.",
        "It was a pleasure chatting with you. Goodbye!",
        "Have a great day! See you next time.",
        "See you soon! I’ll be waiting for our next conversation.",
    ]

    message = random.choice(farewells)

    # Say goodbye
    await robot.say(message).started()

    # Friendly wave with both arms
    await robot.wave(arm=Arm.BOTH).started()

    # Short pause to avoid overlap between motion and speech
    await asyncio.sleep(1.5)

    # Optional closing phrase (also random)
    closing_lines = [
        "Take care!",
        "See you around!",
        "Stay awesome!",
        "Until next time!",
        "Be well!",
    ]
    closing = random.choice(closing_lines)
    await robot.say(closing).completed()
