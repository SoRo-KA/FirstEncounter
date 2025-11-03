from __future__ import annotations

# =========================
# ======== SETUP ==========
# =========================

ROBOT_IP = "localhost"          # IP du robot Mirokai
ROBOT_API_KEY = "admin"    # Clé API
DEFAULT_MODE = "real"              # "real" ou "sim"
OUTPUT_BASE_DIR = "runs"          # Dossier de sauvegarde principal

# Websockets à activer
ENABLED_TOPICS = [
    "semantic_memory",
    "current_focus",
    "head_mode",
    "entities",
    "llm_enabled",
]

# Gestion des images
ENABLE_IMAGES = False               # Active ou désactive la capture d'images
IMAGE_CAPTURE_INTERVAL = 5.0       # Intervalle en secondes entre les captures automatiques

# =========================
# ======== CODE ===========
# =========================



import argparse
import asyncio
import contextlib
import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, Optional
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
from rich import box


@dataclass
class SharedState:
    latest: Dict[str, Any] = field(default_factory=dict)
    previous_values: Dict[str, Any] = field(default_factory=dict)   # ← NEW
    errors: list[str] = field(default_factory=list)

    def set_latest(self, topic: str, value: Any) -> bool:
        """Update topic value if it changed. Return True if it's new."""
        ts = datetime.now().isoformat(timespec="seconds")

        # Compare JSON dumps (stable representation)
        prev = self.previous_values.get(topic)
        serialized = json.dumps(value, sort_keys=True, ensure_ascii=False)
        if prev == serialized:
            return False  # identical → skip recording

        # Store new value
        self.previous_values[topic] = serialized
        self.latest[topic] = {"time": ts, "value": value}
        return True


    def add_error(self, msg: str) -> None:
        ts = datetime.now().isoformat(timespec="seconds")
        self.errors.append(f"[{ts}] {msg}")
        if len(self.errors) > 50:
            self.errors[:] = self.errors[-50:]


class JsonlWriter:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.queue: asyncio.Queue[dict] = asyncio.Queue()
        self._task: Optional[asyncio.Task] = None

    async def start(self) -> None:
        self._task = asyncio.create_task(self._worker(), name=f"writer:{self.path.name}")

    async def stop(self) -> None:
        if self._task:
            self._task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._task

    async def write(self, data: Any) -> None:
        item = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "data": data,
        }
        await self.queue.put(item)

    async def _worker(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        loop = asyncio.get_running_loop()
        while True:
            item = await self.queue.get()
            line = json.dumps(item, ensure_ascii=False)
            await loop.run_in_executor(None, self._append_line, line)

    def _append_line(self, line: str) -> None:
        with self.path.open("a", encoding="utf-8") as f:
            f.write(line + "\n")


import cv2
import numpy as np
import asyncio
import contextlib
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


class Screenshotter:
    def __init__(self, robot: Any, out_dir: Path, state) -> None:
        """Handle screenshots using OpenCV."""
        self.robot = robot
        self.out_dir = out_dir
        self.state = state
        self.out_dir.mkdir(parents=True, exist_ok=True)

    async def take(self, reason: str) -> Optional[Path]:
        """Take a screenshot from robot’s video stream and save with OpenCV."""
        filename = f"{datetime.now().strftime('%H%M%S')}_{reason}.jpg"
        path = self.out_dir / filename
        try:
            vsm = getattr(self.robot, "video_stream_manager", None)
            if vsm is None:
                raise RuntimeError("video_stream_manager unavailable")

            # Try to capture a frame (async or sync depending on robot API)
            frame = None
            if hasattr(vsm, "capture_frame"):
                frame = await vsm.capture_frame()  # async call
            elif hasattr(vsm, "get_frame"):
                frame = vsm.get_frame()  # sync call

            if frame is not None:
                saved = await self._save_frame_cv2(frame, path)
                if saved:
                    return path

            # If capture fails, write placeholder text file
            await self._write_placeholder(path)
            return path

        except Exception as e:  # noqa: BLE001
            self.state.add_error(f"Screenshot error: {e}")
            with contextlib.suppress(Exception):
                await self._write_placeholder(path)
            return None

    async def _save_frame_cv2(self, frame: Any, path: Path) -> bool:
        """Save a frame using OpenCV (cv2.imwrite)."""
        try:
            loop = asyncio.get_running_loop()

            def _save() -> bool:
                # Handle both raw numpy arrays and Pillow images
                if hasattr(frame, "to_numpy"):
                    frame_np = frame.to_numpy()
                elif isinstance(frame, np.ndarray):
                    frame_np = frame
                elif hasattr(frame, "convert"):
                    # Convert Pillow Image to numpy BGR
                    frame_np = cv2.cvtColor(np.array(frame.convert("RGB")), cv2.COLOR_RGB2BGR)
                else:
                    return False
                return cv2.imwrite(str(path), frame_np)

            success = await loop.run_in_executor(None, _save)
            return success
        except Exception as e:
            self.state.add_error(f"cv2 save error: {e}")
            return await self._write_placeholder(path)

    async def _write_placeholder(self, path: Path) -> bool:
        """Write placeholder file when screenshot not available."""
        loop = asyncio.get_running_loop()
        content = b"Placeholder screenshot (no video available).\n"
        await loop.run_in_executor(None, path.write_bytes, content)
        return True


class Dashboard:
    def __init__(self, state):
        self.state = state
        self.console = Console()

    async def run(self):
        with Live(self._render(), refresh_per_second=5, console=self.console) as live:
            try:
                while True:
                    live.update(self._render())
                    await asyncio.sleep(0.2)
            except asyncio.CancelledError:
                return

    def _render(self):
        table = Table(title="[bold cyan]Mirokai Live Dashboard[/]", box=box.ROUNDED)
        table.add_column("Topic", justify="right", style="bold magenta")
        table.add_column("Time", style="dim")
        table.add_column("Value", overflow="fold")

        for topic in ENABLED_TOPICS:
            data = self.state.latest.get(topic, {})
            ts = data.get("time", "-")
            val = data.get("value", {})
            snippet = json.dumps(val, ensure_ascii=False)[:120]
            table.add_row(topic, ts, snippet)

        errors = "\n".join(self.state.errors[-5:]) or "Aucune erreur"
        panel = Panel(errors, title="Erreurs", style="red", box=box.MINIMAL)
        layout = Table.grid(expand=True)
        layout.add_row(table)
        layout.add_row(panel)
        return layout


async def run_real(args: argparse.Namespace, out_dir: Path) -> None:
    from pymirokai.robot import connect  # type: ignore
    async with connect(ROBOT_API_KEY, ROBOT_IP) as robot:
        #robot.video_stream_manager.add_stream(stream_name="head_color", stream_url="head_color")
        #robot.video_stream_manager.add_stream(stream_name="head_debug", stream_url="head_debug")

        # Optional: enable live display if you want visual confirmation
        # robot.video_stream_manager.set_display("head_color", True)
        # robot.video_stream_manager.set_display("head_debug", True)

        # Now continue with your collector logic
        await run_common(robot, out_dir, args)


async def run_sim(args: argparse.Namespace, out_dir: Path) -> None:
    robot = SimulatedRobot()
    async with robot:
        await run_common(robot, out_dir, args)


async def run_common(robot: Any, out_dir: Path, args: argparse.Namespace) -> None:
    state = SharedState()
    writers: dict[str, JsonlWriter] = {t: JsonlWriter(out_dir / f"{t}.jsonl") for t in ENABLED_TOPICS if t != "llm_enabled"}
    for w in writers.values():
        await w.start()

    screenshotter = Screenshotter(robot, out_dir / "screenshots", state)

    def safe_callback(topic: str, fn: Callable[[dict], None]) -> Callable[[dict], None]:
        def wrapper(message: dict) -> None:
            try:
                fn(message)
            except Exception as e:  # noqa: BLE001
                state.add_error(f"Callback '{topic}' error: {e}")
        return wrapper

    async def subscribe(topic: str, cb: Callable[[dict], None]) -> None:
        robot.register_callback(topic, safe_callback(topic, cb))
        await robot.subscribe(topic)

    async def on_semantic(msg: dict) -> None:
        if not state.set_latest("semantic_memory", msg):
            return  # unchanged, skip
        await writers["semantic_memory"].write(msg)
        roles = _extract_roles(msg)
        if ENABLE_IMAGES and any(r in roles for r in ("user", "assistant")):
            await screenshotter.take("conv")

    callbacks = {
        "semantic_memory": lambda m: asyncio.create_task(on_semantic(m)),
        **{t: lambda m, t=t: asyncio.create_task(_generic_callback(state, writers, t, m)) for t in ENABLED_TOPICS if t != "semantic_memory"},
    }

    for topic, cb in callbacks.items():
        await subscribe(topic, cb)

    # Capture automatique à fréquence définie
    if ENABLE_IMAGES:
        asyncio.create_task(_periodic_capture(screenshotter))

    dash = Dashboard(state)
    dash_task = asyncio.create_task(dash.run(), name="dashboard")


    try:
        await asyncio.Future()
    except KeyboardInterrupt:
        pass
    finally:
        for w in writers.values():
            await w.stop()


async def _generic_callback(state, writers, topic, msg):
    changed = state.set_latest(topic, msg)
    if changed and topic in writers:
        await writers[topic].write(msg)


async def _periodic_capture(screenshotter):
    while True:
        try:
            await screenshotter.take("auto")
        except Exception:
            pass
        await asyncio.sleep(IMAGE_CAPTURE_INTERVAL)


def _extract_roles(semantic_msg: dict) -> set[str]:
    roles: set[str] = set()
    try:
        items = semantic_msg.get("memory") or semantic_msg.get("messages") or []
        for it in items:
            role = it.get("role")
            if isinstance(role, str):
                roles.add(role)
    except Exception:
        pass
    return roles


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Mirokai Data Collector")
    p.add_argument("--mode", choices=["real", "sim"], default=DEFAULT_MODE)
    p.add_argument("--ip", type=str, default=ROBOT_IP)
    p.add_argument("--api-key", type=str, default=ROBOT_API_KEY)
    p.add_argument("--out", type=Path, default=Path(OUTPUT_BASE_DIR))
    return p.parse_args()


def make_run_dir(base: Path) -> Path:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = base / ts
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


async def amain() -> None:
    args = parse_args()
    out_dir = make_run_dir(args.out)
    if args.mode == "real":
        await run_real(args, out_dir)
    else:
        await run_sim(args, out_dir)


if __name__ == "__main__":
    try:
        asyncio.run(amain())
    except KeyboardInterrupt:
        pass