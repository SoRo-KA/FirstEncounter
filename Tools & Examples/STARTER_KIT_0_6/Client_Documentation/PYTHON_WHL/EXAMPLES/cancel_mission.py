"""
    Example file show how to cancel a mission
"""

import argparse
import logging
import asyncio
import os
from dotenv import load_dotenv
from pymirokai.robot import connect, Robot
from pymirokai.utils.get_local_ip import get_local_ip
from pymirokai.utils.run_until_interruption import run_until_interruption

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pymirokai_test")


async def run(ip: str, api_key: str) -> None:
    """Run the robot and demonstrate moving forward and cancelling the movement."""
    async with connect(ip=ip, api_key=api_key) as robot:
        await robot_behavior(robot)


async def robot_behavior(robot: Robot) -> None:
    """Demonstrate moving forward and cancelling the movement."""
    mission = robot.move_forward(distance_meters=10.0)
    await mission.started()
    logger.info("Move forward started")

    await asyncio.sleep(10)
    logger.info("Cancelling move forward...")
    await mission.cancel_and_complete()
    logger.info("Move forward cancelled")

    await mission.completed(ignore_exceptions=True)
    logger.info("Move forward finished")


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
