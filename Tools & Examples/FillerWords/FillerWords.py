import asyncio
import random
from pymirokai.robot import connect

LAST_HASH = None
ROBOT = None

FILLERS = [
    "Hmm, let me think…",
    "Okay, give me a sec…",
    "Hmm, I'm on it…",
    "Hmm…",
    "Okay…",
    "Alright…",
    "Let me see…",
    "One sec…",
    "Got it…",
    "Hmm, okay…",
    "Hmm, thinking…",
    "Let me think…",
    "Working on it…",
    "I'm checking…",
    "Just a moment…",
    "Give me a sec…",
    "I'm on it…",
    "Hold on…",
]


async def on_ASR(robot, value: str) -> None:
    """Called only when an ASR message (user speech) is detected."""
    try:
        filler = random.choice(FILLERS)
        mission = robot.say(filler)

        # try starting the mission, but don't crash if voice is busy
        try:
            await mission.started(ignore_exceptions=True)
        except Exception as e:
            print(f"[WARN] Could not start filler voice: {e}")

    except Exception as e:
        print(f"[ERROR in on_ASR]: {e}")


async def pretty_print_event(event: dict) -> None:
    try:
        etype = event.get("type")

        if etype == "PerceptionEvent" and event.get("perception_type") == "ASR":
            text = event.get("value")
            print(f'[ASR] : "{text}"')

            if LAST_HASH is not None:
                # run ASR handler safely
                asyncio.create_task(on_ASR(ROBOT, text))

            return

        if etype == "TTSEvent":
            print(f'[TTS] : "{event.get("value")}"')
            return

        if etype == "MissionEvent":
            print(f'[MISSION] : {event.get("name")}')
            return

        print(f"[OTHER] {etype} -> {event}")

    except Exception as e:
        print(f"[ERROR in pretty_print_event]: {e}")


async def on_semantic_memory(message: dict) -> None:
    global LAST_HASH
    try:
        data = message.get("data", [])
        if not data:
            return

        last = data[-1]

        new_hash = (last.get("type"), last.get("timestamp"))
        if new_hash == LAST_HASH:
            return

        await pretty_print_event(last)
        LAST_HASH = new_hash

    except Exception as e:
        print(f"[ERROR in on_semantic_memory]: {e}")


async def main() -> None:
    global ROBOT

    ip = "localhost"
    api_key = "admin"

    async with connect(api_key, ip) as robot:
        ROBOT = robot

        # Register callback safely into asyncio tasks
        robot.register_callback(
            "semantic_memory",
            lambda msg: asyncio.create_task(on_semantic_memory(msg))
        )

        await robot.subscribe("semantic_memory")

        print("Listening to semantic memory...\n")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
