"""
    Example file to test robot abilities using coroutines (asynchronous way).
    /!\ Don't work totally in simulation as the robot can't say anything yet
"""

import argparse
import logging
import asyncio
import os
from pprint import pformat
from dotenv import load_dotenv
from pymirokai.robot import connect, Robot
from pymirokai.models.data_models import Coordinates
from pymirokai.utils.get_local_ip import get_local_ip
from pymirokai.utils.run_until_interruption import run_until_interruption

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pymirokai_test")

# Global variable to remember state and display only when value changes
navigation_state = None


async def run(ip: str, api_key: str) -> None:
    """Run the robot, demonstrating various features."""
    async with connect(ip=ip, api_key=api_key) as robot:
        # Subscribe to topics
        await robot.subscribe("navigation_state")

        # Register callbacks for topics
        robot.register_callback("navigation_state", handle_navigation_state)

        logger.info("=========== TESTING FEATURES ===========")
        await test_features(robot)

        await asyncio.Future()  # Wait indefinitely


async def test_features(robot: Robot) -> None:
    """Demonstrate various features."""
    response = await robot.set_obstacle_avoidance(True)
    logger.info(f"Command successful: {response}")
    response = await robot.set_robot_max_velocity(50)
    logger.info(f"Command successful: {response}")
    move_mission = robot.go_to_relative(Coordinates(x=1.5, y=-0.5, z=3.14))
    await robot.say("Hello, world!").completed()
    logger.info("Say hello world completed")
    await move_mission.completed()
    logger.info("Move completed")


def handle_navigation_state(message: dict) -> None:
    """Handle updates to the navigation state."""
    global navigation_state
    if message != navigation_state:
        logger.info(f"Navigation State: {pformat(message['data'])}")
        navigation_state = message


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
    args = parser.parse_args()
    await run(ip=args.ip, api_key=args.api_key)


if __name__ == "__main__":
    run_until_interruption(main)
