import random
from pymirokai.decorators.skill import skill
from pymirokai.enums.enums import AccessLevel
from pymirokai.robot import Robot


@skill(
    access_level=AccessLevel.USER,
    verbal_descriptions={
        "en": ["who made you", "who are your creators", "who built you"],
        "fr": ["qui t'a fabriqué", "qui t'a inventé", "qui t'a créé"],
    },
)
async def answer_creators(robot: Robot) -> None:
    """Robot answers who created it, choosing randomly among several responses."""
    responses = [
        "I've been created by Enchanted Tools, and programmed here in Saudi by a team mixed with Kasckt and Sananga Technology. They're like my virtual parents!",
        "I was built by Enchanted Tools, with help from a passionate team here in Saudi Arabia — Kasckt and Sananga Technology!",
        "My creators are Enchanted Tools, and my local training team comes from Kasckt and Sananga Technology.",
        "Enchanted Tools made me, and the Saudi teams from Kasckt and Sananga Technology gave me life here!",
        "I come from Enchanted Tools, with a little Saudi magic from Kasckt and Sananga Technology!",
    ]
    answer = random.choice(responses)
    await robot.say(answer).completed()
