"""
    Example file to test robot abilities without coroutines (synchronous way).
    /!\ Don't work, but here as an example of synchronous coding
"""

import argparse
import logging
import threading
import time
import os
from pprint import pformat
from dotenv import load_dotenv
from pymirokai.robot import Robot
from pymirokai.models.data_models import Coordinates
from pymirokai.utils.get_local_ip import get_local_ip

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pymirokai_test")
robot = Robot()

# Global variable to remember state and display only when value changes
navigation_state = None


def run(ip: str, api_key: str) -> None:
    """Run the robot, demonstrating various features."""
    logger.info("======= CONNECTING TO THE ROBOT =======")
    robot.connect(ip, api_key)

    # Subscribe to topics
    robot.subscribe("navigation_state")

    # Register callbacks for topics
    robot.register_callback("navigation_state", handle_navigation_state)

    logger.info("=========== TESTING FEATURES ===========")
    action_thread = threading.Thread(target=test_features, name="action_thread")
    action_thread.start()

    try:
        while robot.running.is_set():
            time.sleep(1)  # waiting for interruption
    except KeyboardInterrupt:
        logging.warning("=== CLOSING CONNECTION TO THE ROBOT ===")
        robot.connection.cancel()


def test_features() -> None:
    """Demonstrate various features."""
    response = robot.set_obstacle_avoidance(True)
    logger.info(f"Command successful: {response}")
    response = robot.set_robot_max_velocity(50)
    logger.info(f"Command successful: {response}")
    response = robot.go_to_relative(Coordinates(x=1.5, y=-0.5, z=3.14))
    logger.info("Robot moving")
    time.sleep(1)
    response = robot.say("Hello, world!")
    logger.info("Robot saying hello world")


def handle_navigation_state(message: dict) -> None:
    """Handle updates to the navigation state."""
    global navigation_state
    if message != navigation_state:
        logger.info(f"Navigation State: {pformat(message['data'])}")
        navigation_state = message


if __name__ == "__main__":
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
    run(args.ip, args.api_key)
