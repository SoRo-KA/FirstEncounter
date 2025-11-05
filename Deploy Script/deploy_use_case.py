#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deploy a full Use Case (Prompts + Custom Skills) on the Mirokai robot.

Usage:
    python deploy_use_case.py --ip localhost --api-key admin --use-case "Base Demo"
    python deploy_use_case.py --simulate --use-case "Base Demo"
"""

import asyncio
import argparse
import logging
import sys
from pathlib import Path

import coloredlogs
from typing import Any, Dict

from aiohttp import FormData

try:
    from pymirokai.robot import connect, Robot
except ImportError:
    connect = None
    Robot = None


# === Logging Setup ===
coloredlogs.install(
    level="INFO",
    fmt="[%(asctime)s] [%(levelname)s] (%(threadName)s) %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("deploy")


# === Simulated Robot (for --simulate mode) ===
class SimulatedRobot:
    class FakeAPI:
        async def list_skill_files(self):
            return {"skills": [{"name": "demo_skill"}]}

        async def remove_skill_file(self, name):
            await asyncio.sleep(0.2)
            return {"status": "removed", "name": name}

        async def upload_skill_file(self, path):
            await asyncio.sleep(0.5)
            return {"message": f"Skill uploaded successfully ({path})"}

        async def enable_skill_file(self, name, enable):
            await asyncio.sleep(0.2)
            return {"message": f"Skill {name} enabled"}

    def __init__(self):
        self.rest_api = self.FakeAPI()

    async def __aenter__(self):
        logger.info("[SIMULATION] Connected to fake robot 🤖")
        return self

    async def __aexit__(self, exc_type, exc, tb):
        logger.info("[SIMULATION] Disconnected from fake robot.")


# === Response Validator ===
def validate_robot_response(response: Dict[str, Any], action: str, file_name: str) -> bool:
    if not response:
        logger.error(f"❌ No response for {action} {file_name}")
        return False

    # Support different API formats
    if any(k in response for k in ("status", "message", "msg")):
        if response.get("status") == "error":
            logger.error(f"❌ {action.capitalize()} failed for {file_name}: {response.get('msg') or response}")
            return False
        logger.info(f"✓ {file_name}: {response.get('message', 'OK')}")
        return True

    logger.warning(f"⚠️ Unknown response format for {file_name}: {response}")
    return True


# === Core Steps ===
async def remove_all_skills(robot) -> None:
    """Remove all existing skills from the robot safely."""
    logger.info("Fetching existing skills on the robot...")
    skills = await robot.rest_api.list_skill_files()
    skill_list = skills.get("skills", [])

    if not skill_list:
        logger.warning("No skills currently found on the robot.")
        return

    logger.info(f"Found {len(skill_list)} skill(s) to remove.")
    for skill in skill_list:
        # Handle both formats: dict or string
        skill_name = skill["name"] if isinstance(skill, dict) and "name" in skill else str(skill)
        if not skill_name:
            continue

        logger.info(f"→ Removing skill: {skill_name}")
        try:
            await robot.rest_api.remove_skill_file(skill_name)
        except Exception as e:
            logger.error(f"Failed to remove skill {skill_name}: {e}")

async def upload_and_enable_skills(robot, skills_path: Path):
    if not skills_path.exists():
        logger.warning(f"Custom Skills folder not found: {skills_path}")
        return

    skill_files = list(skills_path.glob("*.py"))
    if not skill_files:
        logger.warning("No custom skill files found.")
        return

    logger.info(f"Uploading {len(skill_files)} custom skill(s)...")
    for skill_file in skill_files:
        try:
            res = await robot.rest_api.upload_skill_file(str(skill_file))
            validate_robot_response(res, "upload", skill_file.name)
            await robot.rest_api.enable_skill_file(skill_file.stem, True)
        except Exception as e:
            logger.error(f"Failed to upload {skill_file.name}: {e}")


async def upload_and_enable_prompts(robot, prompts_path: Path) -> None:
    """Update the robot's current prompt using SystemAdmin.update_prompt()."""
    if not prompts_path.exists():
        logger.warning(f"Prompts folder not found: {prompts_path}")
        return

    prompt_files = list(prompts_path.glob("*.txt"))
    if not prompt_files:
        logger.warning("No prompt files found.")
        return

    logger.info(f"Uploading {len(prompt_files)} prompt(s)...")

    for prompt_file in prompt_files:
        logger.info(f"→ Updating prompt from file: {prompt_file.name}")
        try:
            # Lire le contenu du prompt
            with open(prompt_file, "r", encoding="utf-8") as f:
                content = f.read().strip()

            # Appel à la méthode officielle SystemAdmin.update_prompt()
            mission = robot.update_prompt(content)
            await mission.completed()

            logger.info(f"✓ Updated robot prompt with {prompt_file.name}")

        except AttributeError:
            logger.error("❌ The robot does not expose SystemAdmin.update_prompt(). Check firmware or permissions.")
            return
        except Exception as e:
            logger.error(f"Failed to update prompt {prompt_file.name}: {e}")


# === Main Deployment ===
async def deploy_use_case(ip: str, api_key: str, use_case_name: str, simulate: bool = False):
    base_path = Path(__file__).resolve().parents[1] / "Use cases" / use_case_name
    prompts_path = base_path / "Prompt"
    skills_path = base_path / "Skills"

    logger.info(f"=== 🚀 Deploying Use Case: {use_case_name} ===")

    robot_class = SimulatedRobot if simulate else connect

    async with (robot_class() if simulate else connect(api_key, ip)) as robot:
        logger.info("Connected to robot ✅" if not simulate else "Running in SIMULATION mode ⚙️")

        await remove_all_skills(robot)
        await upload_and_enable_skills(robot, skills_path)
        await upload_and_enable_prompts(robot, prompts_path)

        logger.info(f"🎉 Deployment of '{use_case_name}' completed successfully!")


def main():
    parser = argparse.ArgumentParser(description="Deploy a full use case to the robot.")
    parser.add_argument("--ip", help="IP address of the robot.")
    parser.add_argument("--api-key", help="API key for the robot.")
    parser.add_argument("--use-case", required=True, help="Name of the use case to deploy.")
    parser.add_argument("--simulate", action="store_true", help="Run in simulation mode (no robot connection).")
    args = parser.parse_args()

    try:
        asyncio.run(deploy_use_case(args.ip, args.api_key, args.use_case, simulate=args.simulate))
    except KeyboardInterrupt:
        logger.warning("Deployment interrupted by user.")
        sys.exit(1)
    except Exception as e:
        logger.critical(f"Deployment failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
