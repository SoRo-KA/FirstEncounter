"""
    Example file to test robot video.
    /!\ Don't work in simulation
"""

import argparse
import asyncio
import logging
import os
from dotenv import load_dotenv
from pymirokai.robot import connect
from pymirokai.utils.get_local_ip import get_local_ip
from pymirokai.utils.run_until_interruption import run_until_interruption

logger = logging.getLogger("pymirokai")


async def run(ip: str, api_key: str) -> None:
    """Run the robot, demonstrating various features."""
    async with connect(ip=ip, api_key=api_key) as robot:
        robot.video_stream_manager.add_stream(stream_name="head_color", stream_url="head_color")
        robot.video_stream_manager.add_stream(stream_name="head_debug", stream_url="head_debug")
        robot.video_stream_manager.set_display("head_color", True)
        robot.video_stream_manager.set_display("head_debug", True)
        await asyncio.sleep(10)
        robot.video_stream_manager.set_display("head_debug", False)
        robot.video_stream_manager.set_display("head_color", False)
        await asyncio.Future()  # Wait indefinitely


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
