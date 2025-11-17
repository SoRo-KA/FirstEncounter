"""
Skill: tell_joke
Mirokai tells a simple joke from a fixed list.

Behavior:
- Pick one random joke (setup + punchline).
- Say setup, wait 3 seconds, then say punchline.
- After the joke:
  * Wriggle ears
  * Laugh face reaction
  * Play a happy cooing sound (if available)
  * Say: "I hope that made you smile!"
"""

from __future__ import annotations

import asyncio
import random
from typing import Dict

from pymirokai.decorators.skill import skill
from pymirokai.enums.enums import AccessLevel, FaceAnim
from pymirokai.robot import Robot


PAUSE_SECONDS: float = 2.0

JOKES = [
    {
        "setup": "Why don’t scientists trust atoms?",
        "punchline": "Because they make up everything!",
    },
    {
        "setup": "I tried to catch fog yesterday.",
        "punchline": "Mist!",
    },
    {
        "setup": "Why was the math book sad?",
        "punchline": "Because it had too many problems.",
    },
    {
        "setup": "Why do cows have hooves instead of feet?",
        "punchline": "Because they lactose!",
    },
    {
        "setup": "Why did the computer go to the doctor?",
        "punchline": "It had a virus!",
    },
    {
        "setup": "Why do programmers prefer dark mode?",
        "punchline": "Because light attracts bugs!",
    },
]


def pick_joke() -> Dict[str, str]:
    """Pick a random joke from the list."""
    return random.choice(JOKES)

@skill(
    access_level=AccessLevel.USER,
    verbal_descriptions={
        "en": ["tell a joke", "joke", "make me laugh", "say a joke"],
        "fr": ["raconte une blague", "blague", "fais moi rire"],
    },
    parameters=[],
)
async def tell_joke(robot: Robot) -> None:
    """
    Tell a single joke with a pause before the punchline.

    This skill does not return anything; it only makes the robot act and speak.
    """
    joke = pick_joke()
    setup = joke["setup"]
    punchline = joke["punchline"]

    await robot.play_face_reaction(FaceAnim.HAPPY_BIG_SMILE).completed()
    await robot.say(setup).completed()
    await asyncio.sleep(PAUSE_SECONDS)
    await robot.say(punchline).completed()

    try:
        await robot.wriggle_ears().started()
        await robot.play_face_reaction(FaceAnim.HAPPY_BIG_SMILE).completed()
    except Exception:
        pass

    await robot.say("I hope that made you smile!").completed()
    await robot.soft_coo().started()

