"""
Rock-Paper-Scissors interactive skill for Mirokai.
"""

import asyncio
import random
from pymirokai.decorators.skill import skill
from pymirokai.enums.enums import AccessLevel, Hand, FaceAnim
from pymirokai.robot import Robot


@skill(
    access_level=AccessLevel.USER,
    verbal_descriptions={
        "en": ["play rock paper scissors", "rock paper scissors", "rps game"],
        "fr": ["jouer pierre feuille ciseaux", "pierre feuille ciseaux"],
    },
)
async def play_rock_paper_scissors(robot: Robot) -> dict:
    """Play an interactive round of Rock-Paper-Scissors with the user."""
    try:
        # Initial intro sequence
        await robot.arms_down().completed()
        await robot.say("Let's play Rock, Paper, Scissors!").completed()
        await robot.give_hand().completed()
        await asyncio.sleep(0.5)

        # Warm-up gesture sequence
        for move in ["Rock", "Paper", "Scissors"]:
            await robot.say(move + "!").completed()
            if move == "Rock":
                motion = robot.close_hand(Hand.LEFT)
            elif move == "Paper":
                motion = robot.open_hand(Hand.LEFT)
            else:
                motion = robot.wriggle_ears()
            await motion.started()
            await motion.completed()
            await asyncio.sleep(0.2)

        # Short pause before the real round
        await asyncio.sleep(1)

        # Begin round 1
        await robot.say("Round one!").completed()
        await asyncio.sleep(0.5)

        for move in ["Rock", "Paper", "Scissors"]:
            await robot.say(move + "!").completed()
            await asyncio.sleep(0.5)

        # Robot chooses randomly
        robot_choice = random.choice(["rock", "paper", "scissors"])

        # Perform the chosen action
        if robot_choice == "rock":
            motion = robot.close_hand(Hand.LEFT)
        elif robot_choice == "paper":
            motion = robot.open_hand(Hand.LEFT)
        else:
            motion = robot.wriggle_ears()

        await motion.started()
        await motion.completed()
        await robot.say(f"I choose {robot_choice}!").completed()

        # Ask for the user's choice
        await robot.say("What did you choose?").completed()

        await asyncio.sleep(1)
        await robot.arms_down().completed()
    
        await robot.say("Win or lose in RPS, friendship stays undefeated!").completed()
        await robot.play_face_reaction(FaceAnim.HAPPY_BIG_SMILE).completed()
        await robot.say("I hope you enjoyed the game! What would you like to explore or play next?").completed()

        return {}


    except Exception as e:
        await robot.say(f"Oops! Something went wrong: {e}").completed()
        return {}


