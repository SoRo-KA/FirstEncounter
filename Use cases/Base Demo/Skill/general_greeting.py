from pymirokai.robot import Robot
from pymirokai.decorators.skill import skill
from pymirokai.enums.enums import AccessLevel
from pymirokai.enums.enums import Arm


@skill(
    access_level=AccessLevel.USER,
    verbal_descriptions={
        "en": [
            "hello", "hi", "hey", "greetings", "greeting", "howdy", "yo", "hiya", "sup",
            "what's up", "salutations"
        ],
        "fr": ["salut", "bonjour", "coucou", "hey"],
    },
)
async def general_greeting(robot: Robot) -> dict:
    """Welcome the user with gestures and offer assistance."""
    
    # Speak welcome
    message = "Hello and welcome! I'm happy to see you."
    await robot.say(message).started()

    # Perform double wave
    await robot.wave().completed()
    # await robot.animate_arms("HELLO").completed()

    # Ask how to assist
    question = "How may I brighten your day?"
    await robot.say(question).completed()

    return