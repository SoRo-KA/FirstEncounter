import random
from pymirokai.decorators.skill import skill
from pymirokai.enums.enums import AccessLevel
from pymirokai.robot import Robot


@skill(
    access_level=AccessLevel.USER,
    verbal_descriptions={
        "en": ["where are you", "where am i", "where is this place"],
        "fr": ["où es-tu", "où suis-je", "où sommes-nous"],
    },
)
async def answer_where_are_you(robot: Robot) -> None:
    """Robot answers where it is located, choosing a random friendly response."""
    responses = [
        "I am at the 3rd Saudi Forum for 4IR 2025 on the booth of the kackst.",
        "Right now I am at the 3rd Saudi Forum for 4IR 2025 – C4IR Saudi Arabia, hosted at Four Seasons Hotel Riyadh.",
        "I am here at the 3rd Saudi Forum for 4IR 2025 with the kackst team.",
        "You are at the 3rd Saudi Forum for 4IR 2025 – C4IR Saudi Arabia, and I am on the kackst booth.",
        "We are at the 3rd Saudi Forum for 4IR 2025 in Riyadh, and this is the kackst booth!",
    ]
    answer = random.choice(responses)
    await robot.say(answer).completed()
