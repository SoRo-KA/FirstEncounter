# simulator.py

from __future__ import annotations

import asyncio
import contextlib
import random
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional


# --- Mission simulée ---
@dataclass
class _Mission:
    async def completed(self) -> dict:
        await asyncio.sleep(0.05)
        return {"result": {"started": True, "awaited": True}}

    async def started(self) -> "_Mission":
        await asyncio.sleep(0.01)
        return self


class _VideoManager:
    """Fournit une interface compatible avec Screenshotter."""

    async def capture_frame(self) -> Any:
        # retourne un placeholder PIL.Image si PIL dispo, sinon bytes
        try:
            from PIL import Image, ImageDraw  # type: ignore

            img = Image.new("RGB", (320, 240), color=(200, 200, 200))
            d = ImageDraw.Draw(img)
            d.text((10, 10), "Simulated Frame", fill=(0, 0, 0))
            return img
        except Exception:
            return b"SIM_FRAME"


class SimulatedRobot:
    def __init__(self) -> None:
        self._callbacks: Dict[str, list[Callable[[dict], None]]] = {}
        self._tasks: list[asyncio.Task] = []
        self.video_stream_manager = _VideoManager()

    async def __aenter__(self) -> "SimulatedRobot":
        # démarrer les producteurs
        self._tasks.append(asyncio.create_task(self._produce_focus()))
        self._tasks.append(asyncio.create_task(self._produce_head_mode()))
        self._tasks.append(asyncio.create_task(self._produce_entities()))
        self._tasks.append(asyncio.create_task(self._produce_semantic()))
        self._tasks.append(asyncio.create_task(self._produce_llm()))
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:  # noqa: D401
        for t in self._tasks:
            t.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await t

    # --- API compat ---
    def register_callback(self, topic: str, cb: Callable[[dict], None]) -> None:
        self._callbacks.setdefault(topic, []).append(cb)

    async def subscribe(self, topic: str) -> None:
        # rien à faire côté simulateur, mais on valide l'API
        await asyncio.sleep(0)

    def _emit(self, topic: str, payload: dict) -> None:
        for cb in self._callbacks.get(topic, []):
            try:
                cb(payload)
            except Exception:
                pass

    def say(self, text: str) -> _Mission:
        # Emit assistant message into semantic_memory stream
        self._emit(
            "semantic_memory",
            {
                "memory": [
                    {"role": "assistant", "content": text},
                ]
            },
        )
        return _Mission()

    # --- Producers ---
    async def _produce_focus(self) -> None:
        choices = ["everything", "humans", "handles", "deposit_zone", "firefly"]
        while True:
            self._emit("current_focus", {"focus": random.choice(choices)})
            await asyncio.sleep(1.0)

    async def _produce_head_mode(self) -> None:
        choices = ["animate", "track", "freeze", "scan", "auto"]
        while True:
            self._emit("head_mode", {"mode": random.choice(choices)})
            await asyncio.sleep(1.3)

    async def _produce_entities(self) -> None:
        base = ["apple", "banana", "chair", "person", "door"]
        while True:
            sample = random.sample(base, k=random.randint(1, 3))
            self._emit("entities", sample)
            await asyncio.sleep(2.0)

    async def _produce_semantic(self) -> None:
        user_utts = [
            "Bonjour Mirokai !",
            "Peux-tu me montrer le chemin ?",
            "Quelle est la batterie ?",
        ]
        while True:
            # user speaks
            self._emit(
                "semantic_memory",
                {"memory": [{"role": "user", "content": random.choice(user_utts)}]},
            )
            await asyncio.sleep(2.5)
            # assistant responds via say()
            self.say("Je t'écoute.")
            await asyncio.sleep(2.5)

    async def _produce_llm(self) -> None:
        val = False
        while True:
            val = not val
            self._emit("llm_enabled", {"enabled": val})
            await asyncio.sleep(5)

