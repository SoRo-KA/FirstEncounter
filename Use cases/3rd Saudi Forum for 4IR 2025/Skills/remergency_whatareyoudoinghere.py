import random
from pymirokai.decorators.skill import skill
from pymirokai.enums.enums import AccessLevel
from pymirokai.robot import Robot


@skill(
    access_level=AccessLevel.USER,
    verbal_descriptions={
        "en": ["what are you doing here", "why are you here", "what is your purpose here"],
        "fr": ["que fais-tu ici", "pourquoi es-tu ici", "quelle est ta mission ici"],
    },
)
async def answer_purpose_here(robot: Robot) -> None:
    """Robot explains why it is here, choosing a random response."""
    responses = [
        "I am here to welcome visitors and show my skills at the 3rd Saudi Forum!",
        "I'm here to demonstrate what I can do and meet new people at the 3rd Saudi Forum!",
        "My purpose is to represent Enchanted Tools and share what Mirokai can do here at the forum!",
        "I'm here to interact with visitors and show my abilities at the 3rd Saudi Forum!",
        "I'm here to make everyone smile and discover what I can do at this amazing Saudi Forum!",
    ]
    answer = random.choice(responses)
    await robot.say(answer).completed()
