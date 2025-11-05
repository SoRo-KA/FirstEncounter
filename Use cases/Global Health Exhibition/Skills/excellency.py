import requests
from pymirokai.decorators.skill import skill, ParameterDescription
from pymirokai.enums.enums import AccessLevel, FaceAnim
from pymirokai.robot import Robot


@skill(
    access_level=AccessLevel.USER,  # Defines access level for the skill
    verbal_descriptions={"en": ["excellence", "e1",  "welcome the excellence"]},
)

async def show_capabilities(robot: Robot) -> dict:
    
    try:
        await robot.stop_conversation().completed()
        say = robot.say("Welcome your excellency to the ministry of interior")
        await say.started()
        await robot.animate_arms("HELLO").completed()
        await say.completed()
        await robot.start_conversation().completed()
        # await robot.discover_body().completed()
        # await robot.say("Even more, with a wonderful teams as kackst and Unchated Tools the sky will be the limit").completed()

    except requests.RequestException:
            answer = "I have an issue"

    await robot.play_face_reaction(FaceAnim.HAPPY_BIG_SMILE).completed()
    return {"llm_output": answer}
