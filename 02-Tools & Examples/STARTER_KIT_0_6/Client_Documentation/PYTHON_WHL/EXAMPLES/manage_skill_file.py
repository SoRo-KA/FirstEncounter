'''
    File to manage custom skill files
'''

import argparse
import logging
import os
from dotenv import load_dotenv
from pymirokai.robot import connect, Robot
from pymirokai.utils.get_local_ip import get_local_ip
from pymirokai.utils.run_until_interruption import run_until_interruption

logger = logging.getLogger("pymirokai")


async def run(ip: str, api_key: str) -> None:
    """Interactive tool to manage skill files on the robot"""
    async with connect(ip=ip, api_key=api_key) as robot:
        await interactive_skill_manager(robot)


async def interactive_skill_manager(robot: Robot) -> None:
    """Interactive terminal menu to manage skill files on the robot."""
    while True:
        print("\nSkill Management Menu")
        print("1. Upload a skill script")
        print("2. Enable a script")
        print("3. Disable a script")
        print("4. Remove a script")
        print("5. Exit")
        choice = input("Select an option (1-5): ").strip()

        # List available scripts
        result = await robot.list_skill_files()
        scripts = result.get("skills", [])

        if not scripts:
            print("No scripts found on the robot.")
        else:
            print("\nAvailable scripts on the robot:")
            for idx, name in enumerate(scripts, 1):
                print(f"{idx}. {name}")

        if choice == "1":
            path = input("Enter the path of the script to upload: ").strip()
            if not os.path.exists(path):
                print("File not found.")
                continue
            response = await robot.upload_skill_file(path)
            print("Upload response:", response)

        elif choice == "2":
            if not scripts:
                print("No script found to enable.")
                continue
            name = input("Enter the script name to enable: ").strip()
            if name not in scripts:
                print("Script not found.")
                continue
            response = await robot.enable_skill_file(name, True)
            print("Enable custom skill:", response)

        elif choice == "3":
            if not scripts:
                print("No script found to disable.")
                continue
            name = input("Enter the script name to disable: ").strip()
            if name not in scripts:
                print("Script not found.")
                continue
            response = await robot.enable_skill_file(name, False)
            print("Disable custom skill:", response)

        elif choice == "4":
            if not scripts:
                print("No script found to remove.")
                continue
            name = input("Enter the script name to remove: ").strip()
            if name not in scripts:
                print("Script not found.")
                continue
            confirm = input(f"Are you sure you want to remove '{name}'? (y/n): ").lower()
            if confirm == "y":
                response = await robot.remove_skill_file(name)
                print("Remove custom skill:", response)
            else:
                print("Removal cancelled.")

        elif choice == "5":
            print("Exiting.")
            break
        else:
            print("Invalid option. Please select a number between 1 and 5.")


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
