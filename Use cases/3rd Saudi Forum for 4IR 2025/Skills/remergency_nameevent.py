import random
from pymirokai.decorators.skill import skill
from pymirokai.enums.enums import AccessLevel
from pymirokai.robot import Robot


@skill(
    access_level=AccessLevel.USER,
    verbal_descriptions={
        "en": [
            "what is the name of the forum",
            "what's this event called",
            "what forum is this",
            "what is this conference",
            "what is the name of this forum",
        ],
        "fr": [
            "quel est le nom du forum",
            "comment s'appelle ce forum",
            "quel est le nom de cet événement",
            "c'est quoi ce forum",
        ],
    },
)
async def answer_forum_name(robot: Robot) -> None:
    """Answer when asked for the name of the forum, without dashes or heavy acronyms."""
    responses = [ the Third Saudi Forum for the Fourth Industrial Revolution.
        "The event is called",
        "This is the Third Saudi Forum on the Fourth Industrial Revolution.",
        "You are at the Third Saudi Forum for the Fourth Industrial Revolution in Riyadh.",
        "It is the Third Saudi Forum dedicated to the Fourth Industrial Revolution.",
        "This forum is officially called the Third Saudi Forum for the Fourth Industrial Revolution.",
    ]

    answer = random.choice(responses)
    await robot.say(answer).completed()
