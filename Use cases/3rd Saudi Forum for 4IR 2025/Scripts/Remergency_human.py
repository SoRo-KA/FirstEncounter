import random
from pymirokai.decorators.skill import skill
from pymirokai.enums.enums import AccessLevel
from pymirokai.robot import Robot


@skill(
    access_level=AccessLevel.USER,
    verbal_descriptions={
        "en": ["are you human", "what are you"],
        "fr": ["es-tu humain", "qui es-tu"],
    },
)
async def answer_are_you_human(robot: Robot) -> None:
    """Répond aléatoirement à la question 'Are you human?'."""
    responses = [
        "No, I'm more than that, I'm a Mirokai! I come from the planet Nimira.",
        "Of course not! I’m a Mirokai — something far more interesting than a human.",
        "Not really. I’m a friendly robot from the world of Nimira!",
        "No, but I like humans a lot. They’re fascinating!",
    ]
    answer = random.choice(responses)
    await robot.say(answer).completed()