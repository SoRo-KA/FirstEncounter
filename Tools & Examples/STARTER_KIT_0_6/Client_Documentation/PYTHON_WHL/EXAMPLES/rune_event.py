"""Example file to test robot abilities with runes.
/!\ Don't work in simulation
"""

import argparse
import asyncio
import logging
import os
from dotenv import load_dotenv
from pymirokai.robot import connect, Robot
from pymirokai.mission import MissionError
from pymirokai.utils.get_local_ip import get_local_ip
from pymirokai.utils.run_until_interruption import run_until_interruption

logger = logging.getLogger("pymirokai")

# A global state to track the last detected click type
last_click_state = {}


async def run(ip: str, api_key: str, rune: str) -> None:
    """Run the robot, demonstrating various features."""
    async with connect(ip=ip, api_key=api_key) as robot:
        # Subscribe to topic runes
        await robot.subscribe("runes")

        # Register callback for rune events
        robot.register_callback("runes", lambda msg: asyncio.create_task(rune_event(robot, msg, rune)))

        # Keep the script running indefinitely
        await asyncio.Future()


async def rune_event(robot: Robot, msg: dict, rune: str) -> None:
    """Handle rune events."""
    global last_click_state

    try:
        states = {
            "long_pressed": (await robot.is_long_pressed(rune))["result"],
            "double_clicked": (await robot.is_double_clicked(rune))["result"],
            "clicked": (await robot.is_clicked(rune))["result"],
        }
        if last_click_state is None or last_click_state != states:
            last_click_state = states
            if states["clicked"]:
                await react_click(robot, rune)
            elif states["double_clicked"]:
                await react_double_click(robot, rune)
            elif states["long_pressed"]:
                await react_long_click(robot, rune)

    except MissionError:
        logger.warning("Mission error occurred while handling rune event.")


async def react_click(robot: Robot, rune):
    """Handle single click behavior."""
    await robot.say(f"Rune {rune} clicked").completed()


async def react_double_click(robot: Robot, rune):
    """Handle double click behavior."""
    await robot.say(f"Rune {rune} double clicked").completed()


async def react_long_click(robot: Robot, rune):
    """Handle long press behavior."""
    await robot.say(f"Rune {rune} long pressed").completed()


async def main() -> None:
    """Main entry point for the script."""
    load_dotenv()
    ip = os.getenv("ROBOT_IP")
    if ip:
        logger.info(f"trying to start on host:{ip}")
    else:
        ip = get_local_ip()
        logger.info(f"trying to start on simulation, host:{ip}")
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "-i",
        "--ip",
        help="Set the IP of the robot you want to connect.",
        type=str,
        default=ip,
    )
    parser.add_argument(
        "-k",
        "--api-key",
        help="Set the API key of the robot you want to connect.",
        type=str,
        default=os.getenv("PYMIROKAI_API_KEY", ""),
    )
    parser.add_argument(
        "-r", 
        "--rune_name", 
        help="Rune on which you want to run the behavior.", 
        type=str, 
        default="HANDLEA",
    )
    args = parser.parse_args()

    try:
        await run(args.ip, args.api_key, args.rune_name)
    except Exception as e:
        logger.error(f"Error during execution: {e}")
        exit(1)


if __name__ == "__main__":
    run_until_interruption(main)
