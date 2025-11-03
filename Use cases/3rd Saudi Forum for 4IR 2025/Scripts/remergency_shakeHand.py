import random
from pymirokai.decorators.skill import skill
from pymirokai.enums.enums import AccessLevel
from pymirokai.robot import Robot


@skill(
    access_level=AccessLevel.USER,
    verbal_descriptions={
        "en": ["Shake hande"],
        "fr": ["serrer la main"],
    },
)
async def answer_where_are_you(robot: Robot) -> None:
    """Robot answers where it is located, choosing a random friendly response."""
    responses = [
        "Of course I can!"
    ]
    answer = random.choice(responses)
    await robot.animate_arms("GIVE_HAND_1").started()
    await robot.say(answer).completed()
