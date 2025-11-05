import random
from pymirokai.decorators.skill import skill
from pymirokai.enums.enums import AccessLevel
from pymirokai.robot import Robot


@skill(
    access_level=AccessLevel.USER,
    verbal_descriptions={
        "en": ["what is your name", "who are you", "tell me your name"],
        "fr": ["quel est ton nom", "qui es-tu", "comment tu t'appelles"],
    },
)
async def answer_name(robot: Robot) -> None:
    """Simple Q&A skill — robot only speaks an answer randomly chosen."""
    responses = [
        "I am Mirokai, a friendly robot created by Enchanted Tools.",
        "My name is Mirokai! Nice to meet you.",
        "They call me Mirokai — your companion from Enchanted Tools.",
        "I'm Mirokai, an expressive and curious robot friend.",
        "Mirokai here! Ready to help and chat with you.",
    ]
    answer = random.choice(responses)
    await robot.say(answer).completed()
