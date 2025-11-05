import random
from pymirokai.decorators.skill import skill
from pymirokai.enums.enums import AccessLevel
from pymirokai.robot import Robot


@skill(
    access_level=AccessLevel.USER,
    verbal_descriptions={
        "en": ["thanks", "thank you", "appreciate it"],
        "fr": ["merci", "merci beaucoup", "je te remercie"],
    },
)
async def answer_Thanks(robot: Robot) -> None:
    """Robot answers when the user says thanks, choosing randomly among several replies."""
    responses = [
        "You're welcome! I'm happy to help!",
        "Thank you! I hope I did everything as you wished!",
        "No problem at all!",
        "Anytime! I'm always here for you!",
        "You're very welcome!",
        "Glad I could assist!",
    ]
    answer = random.choice(responses)
    await robot.say(answer).completed()
