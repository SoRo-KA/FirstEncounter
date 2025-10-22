import os
import asyncio
import threading
from typing import Optional

import keyboard  # pip install keyboard

# --- Rich UI ---
from rich.live import Live
from rich.layout import Layout
from rich.table import Table
from rich.panel import Panel
from rich.align import Align
from rich.text import Text

try:
    from pymirokai.enums.enums import AccessLevel, Hand, Arm, FaceAnim
except Exception as e:
    print("Error, pymirokai enums not found")

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

# ---- Logging setup ----
LOG_PATH = Path(__file__).with_name("ilmi_orchestration.log")

logger = logging.getLogger("ILMI")
logger.setLevel(logging.INFO)
handler = RotatingFileHandler(LOG_PATH, maxBytes=1_000_000, backupCount=3, encoding="utf-8")
fmt = logging.Formatter("%(asctime)s.%(msecs)03d [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
handler.setFormatter(fmt)
logger.addHandler(handler)

def log(msg: str):
    logger.info(msg)


# =========================
#  Config robot
# =========================
ROBOT_IP = os.getenv("ROBOT_IP", "192.168.1.203")
API_KEY = os.getenv("ROBOT_API_KEY", "dichogamous-nonmonarchical-syndicate-Polystomidae")
BATTERY_POLL_SECONDS = 5
ROBOT_VOLUME = 85
DEMO_MODE = False

# =========================
#  Adapter Robot
# =========================
class RobotManager:
    def __init__(self, robot_ip: str, api_key: str):
        self.robot_ip = robot_ip
        self.api_key = api_key
        self.connected: bool = False
        self.battery: Optional[int] = None
        self.on_telemetry: Optional[Callable[[], None]] = None

        try:
            from pymirokai.robot import Robot
            self.robot = Robot()  # ← this is the SDK robot instance
            self._use_sim = False
        except Exception as e:
            print(f"[WARN] Using simulator: {e}")
            self.robot = None
            self._use_sim = True

        # Simulated values
        self._sim_battery = 42.69
        self._sim_decay = -1
        self._connection_obj = None

    async def connect(self):
        log("---------------------------------------")
        if self._use_sim:
            await asyncio.sleep(0.5)
            self.connected = True
            log("[ROBOT] SIM connected")
            return

        log(f"[ROBOT] Connecting to {self.robot_ip} …")
        self._connection_obj = self.robot.connect(self.robot_ip, self.api_key)
        await self._connection_obj.connected()
        self.connected = True
        log("[ROBOT] Connected successfully")
        self.robot.subscribe("battery_voltage")

        # Example boot beeps / volume
        try:
            await self.robot.play_animation_sound("meow").completed()
            await self.robot.set_sound_level(ROBOT_VOLUME)
            await self.robot.play_animation_sound("meow").completed()
            log(f"[ROBOT] Volume set to {ROBOT_VOLUME}")
        except Exception as e:
            log(f"[ROBOT] Post-connect init error: {e}")


        def handle_battery_voltage(message: dict) -> None:
            #log(f"[BATTERY CALLBACK] Raw: {message!r}")
            try:
                raw = None
                if isinstance(message, dict):
                    if "data" in message:
                        raw = message["data"]            # <- your payload shape
                    else:
                        for k in ("voltage", "value", "battery", "battery_voltage", "v", "volt"):
                            if k in message:
                                raw = message[k]
                                break
                        if raw is None:
                            for v in message.values():
                                if isinstance(v, (int, float)):
                                    raw = v
                                    break
                else:
                    raw = message

                if raw is None:
                    log("[BATTERY CALLBACK] No numeric voltage found in message")
                    return

                self.battery = round(float(raw), 2)
                #log(f"[BATTERY CALLBACK] Parsed voltage = {self.battery:.2f} V")
            except Exception as e:
                self.battery = None
                log(f"[BATTERY CALLBACK] Parse error: {e}")

            # 🔔 Tell the UI to refresh (thread-safe)
            if callable(self.on_telemetry):
                try:
                    self.on_telemetry()
                except Exception as e:
                    log(f"[BATTERY CALLBACK] on_telemetry error: {e}")



        self.robot.register_callback("battery_voltage", handle_battery_voltage)
        log("[ROBOT] battery_voltage callback registered")
        self.robot.on_telemetry = lambda: self.loop.call_soon_threadsafe(self.live.update, self.render(), True)

async def handle_error(e, robot):
    log(f"[ERROR] {str(e)}")
    if(DEMO_MODE == False):
        await robot.say(str(e)).completed()
# =========================
#  Actions async
# =========================
async def Entrance_and_Greeting(robot):
    try:
        await robot.move_forward(distance_meters=2).started()
        await asyncio.sleep(3)
        await robot.scan_neck_and_wait_infinitely().started()
        await robot.soft_coo().completed()
        hello = robot.say("oh! Hello I'm very happy to be here!! I’m Miroka, your companion in exploration! I can’t promise to know everything, but I’ll never get tired of your questions.")
        await hello.started()
        await robot.play_face_reaction(FaceAnim.AMAZED).started()
        await asyncio.sleep(6)
        await robot.wave().completed()
        await hello.completed()
        # phrase = robot.say("Together with eilmi, we are here to spark curiosity and bring science to life in new ways.")
        # await phrase.completed()
        await robot.take_neck_resource_punctually().completed()
        await asyncio.sleep(1)
        go = robot.say("Dear Sarrah, let's go together in front of this wonderfull audience. Grab my hand!")
        await go.started()
        await robot.animate_arms("HOLD_HAND_0").started()
        await go.completed()
         
         # Left wave
        # left_wave = robot.animate_arm("wave", Arm.LEFT)
        # await left_wave.completed()

        # # Right wave
        # right_wave = robot.animate_arm("wave", Arm.RIGHT)
        # await right_wave.completed() 
    except Exception as e:
        await handle_error(e, robot)

async def ILMI_role(robot):

    try:
        # Phrase 1
        await robot.play_face_reaction(FaceAnim.JOY).started()
        phrase = robot.say("Of course! I guide visitors through stories that deepen their connection to what’s around them.")
        await phrase.started()
        await robot.animate_arms("HOLD_MY_BEER_0").started()
        await phrase.completed()

        # Phrase 2
        await robot.play_face_reaction(FaceAnim.PERPLEXED).started()
        phrase = robot.say("I may not feel the smoothness of coral or breathe in the scent of the desert wind,")
        await phrase.started()
        await asyncio.sleep(2)
        await robot.wriggle_ears().started()
        await phrase.completed()

        # Phrase 3
        await robot.play_face_reaction(FaceAnim.INTEREST).started()
        phrase = robot.say("but I can help others notice and appreciate those details that bring eilmi’s discoveries to life…")
        await phrase.started()
        await robot.arms_down().started()
        await phrase.completed()

        # Phrase 4
        await robot.play_face_reaction(FaceAnim.PRIDE).started()
        phrase = robot.say("I am here to work alongside people to make the experience richer ...")
        await phrase.started()
        await robot.animate_arms("HANDS_ON_HIPS").started()
        await phrase.completed()

        await robot.play_face_reaction(FaceAnim.HAPPY_BIG_SMILE).started()
        phrase = robot.say("like adding another layer of perspective to the customer’s visit.")
        await phrase.started()
        await robot.arms_down().started()
        await phrase.completed()
    except Exception as e:
        await handle_error(e, robot)

async def Red_sea(robot):
    try:
        # Phrase 1: Excitement
        await robot.play_face_reaction(FaceAnim.SURPRISE).started()
        phrase = robot.say(
            "Oh Yes!! One of my favorite stories comes from the Red Sea. "
            "The water there is unusually warm and salty, yet life flourishes."
        )
        await phrase.started()
        await asyncio.sleep(0.3)
        await robot.animate_arms("HAND_CHECK_0").started()
        await asyncio.sleep(1.5)
        await robot.arms_down().started()
        await phrase.completed()

        # Phrase 2 — Admiration and curiosity
        await robot.play_face_reaction(FaceAnim.DAZZLED).started()
        phrase = robot.say(
            "Corals and fish have adapted in remarkable ways ... "
            "small creatures teaching us big lessons about resilience."
        )
        await phrase.started()
        await asyncio.sleep(1.5)
        await robot.wriggle_ears(rounds=2).started()
        await phrase.completed()

        # Phrase 3 — Reflection and hope
        await robot.play_face_reaction(FaceAnim.PRIDE).started()
        phrase = robot.say(
            "Some scientists call these corals heat-tough because they can handle temperatures that would destroy most reefs. "
            "Studying them helps us understand how life might survive in a changing climate. "
            "For me, that story is a reminder that science is not only about knowledge ... it’s also about hope."
        )
        await phrase.started()
        await robot.animate_arms("HANDS_ON_HIPS").started()
        await phrase.completed()

        # Wrap up: Arms down to neutral
        await robot.arms_down().started()
    except Exception as e:
        await handle_error(e, robot)
    
async def Vision2030(robot):
    try:
        # Phrase 1 — Vision and aspiration
        await robot.play_face_reaction(FaceAnim.DETERMINED).started()
        phrase = robot.say("Vision 2030 is about building a creative, knowledge-driven Saudi Arabia.")
        await phrase.started()
        await robot.animate_arms("SHOW_SOMETHING_UP_0").started()
        await phrase.completed()

        # Phrase 2 — ILMI's purpose (no arm movement)
        await robot.play_face_reaction(FaceAnim.INTEREST).started()
        phrase = robot.say("eilmi is part of that vision ... it turns curiosity into learning, and learning into real skills.")
        await phrase.started()
        await robot.arms_down().started()
        await phrase.completed()

        # Phrase 3 — Engagement and future
        await robot.play_face_reaction(FaceAnim.HAPPY_BIG_SMILE).started()
        phrase = robot.say(
            "Here, people don’t just see science; they experience it, create with it, and grow from it. "
            "That’s how eilmi helps shape the future the Kingdom is reaching for."
        )
        await phrase.started()
        await robot.wriggle_ears(rounds=2).started()
        await phrase.completed()

        # Return arms to neutral
        await robot.arms_down().started()
    except Exception as e:
        await handle_error(e, robot)

async def END(robot):
    try:
        # Phrase 1 — Gratitude
        await robot.play_face_reaction(FaceAnim.JOY).started()
        phrase = robot.say("Thank you. If you want to continue the conversation, I’ll be just outside after the session.")
        await phrase.started()
        await robot.arms_down().started()
        await phrase.completed()

        # Phrase 2 — Invitation
        await robot.play_face_reaction(FaceAnim.HAPPY_BIG_SMILE).started()
        phrase = robot.say("I would be happy if you stopped by to talk to me!")
        await phrase.started()
        await phrase.completed()

        # Phrase 3 — Goodbye with double wave
        await robot.play_face_reaction(FaceAnim.PRIDE).started()
        phrase = robot.say("Goodbye everyone!")
        wave = robot.animate_arms("HELLO")
        await robot.scan_neck_and_wait_infinitely().started()
        await wave.started()
        await phrase.started()
        await phrase.completed()
        await wave.completed()
        #await robot.animate_arms("HOLD_HAND_1").started()
        await robot.take_neck_resource_punctually().completed()
        #phrase = robot.say("Let's go outside!")
        #await phrase.completed()


    except Exception as e:
        await handle_error(e, robot)

async def Start_llm(robot):
    try:
        await robot.set_sound_level(0)
        await robot.start_conversation().completed()
        await asyncio.sleep(1.5)
        await robot.set_sound_level(ROBOT_VOLUME)
    except Exception as e:
        await handle_error(e, robot)

async def Stop_llm(robot):
    try:
        await robot.stop_conversation().completed()
    except Exception as e:
        await handle_error(e, robot)

async def Arms_Down(robot):
    await robot.arms_down().completed()

# Map touches -> fonctions
ACTIONS = {
    "1": Entrance_and_Greeting, "num 1": Entrance_and_Greeting,
    "2": ILMI_role, "num 2": ILMI_role,
    "3": Red_sea, "num 3": Red_sea,
    "4": Vision2030, "num 4": Vision2030,
    "5": END, "num 5": END,
    "6": Arms_Down, "num 6": Arms_Down,
    "7": Start_llm, "num 7": Start_llm,
    "8": Stop_llm, "num 8": Stop_llm,
}

# =========================
#  Orchestrateur + UI
# =========================
class Orchestrator:
    def __init__(self, loop: asyncio.AbstractEventLoop, live: Live, robot_mgr: RobotManager):
        self.loop = loop
        self.live = live
        self.robot = robot_mgr

        self.current_task: Optional[asyncio.Task] = None
        self.current_name: Optional[str] = None
        self.key_queue: asyncio.Queue[str] = asyncio.Queue()
        self.last_message: str = "Prêt."

    # -------- UI building --------
    def _build_header(self) -> Panel:
        # Pense-bête 1..8
        ordered = []
        for i in range(1, 9):
            func = ACTIONS[str(i)]
            ordered.append((str(i), func.__name__))

        table = Table(expand=True, show_header=True, header_style="bold")
        table.add_column("Touche", justify="center")
        table.add_column("Fonction")
        for num, fname in ordered:
            table.add_row(num, fname)

        return Panel(table, title="Raccourcis", border_style="cyan")

    def _build_robot_panel(self) -> Panel:
        """Display connection state, battery level, and SIM warning if active."""
        # Connection status
        status = Text("Connecté", style="bold green") if self.robot.connected else Text("Déconnecté", style="bold red")

        # Battery
        if self.robot.battery is None:
            battery_text = Text("Batterie: N/A", style="yellow")
        else:
            voltage = self.robot.battery
            style = "bold green" if voltage >= 26.0 else ("bold yellow" if voltage >= 23.5 else "bold red")
            battery_text = Text(f"Batterie: {voltage:.2f} V", style=style)

        # Combine texts
        lines = Text.assemble(
            Text("Robot\n", style="bold cyan"),
            status, Text("\n"),
            battery_text
        )

        # ⚠️ Add simulation warning
        if getattr(self.robot, "_use_sim", False):
            sim_text = Text("\n\n⚠ SIMULATION MODE ⚠", style="bold yellow on red")
            lines.append_text(sim_text)

        return Panel(
            Align.left(lines),
            border_style="cyan",
            title="Robot",
            title_align="left"
        )


    def _build_status(self) -> Panel:
        if self.current_task and not self.current_task.done():
            text = Text(f"En cours : {self.current_name}", style="bold red")
        else:
            text = Text("IDLE", style="bold green")
        return Panel(Align.center(text), title="ÉTAT", border_style="white")

    def _build_footer(self) -> Panel:
        help_text = Text.from_markup(
            "[b]Contrôles :[/b] 1–8 = lancer | [b]Espace[/b] = annuler | [b]S[/b] = état | [b]Esc[/b] = quitter\n"
            f"[dim]{self.last_message}[/dim]"
        )
        return Panel(help_text, border_style="magenta")

    def render(self):
        root = Layout(name="root")
        top = Layout(name="top")
        body = Layout(name="body")
        bottom = Layout(name="bottom")

        root.split_column(
            top,
            body,
            bottom
        )

        left_top = Layout(name="left_top")
        right_top = Layout(name="right_top", size=32)  # colonne droite étroite
        top.split_row(left_top, right_top)

        left_top.update(self._build_header())
        right_top.update(self._build_robot_panel())
        body.update(self._build_status())
        bottom.update(self._build_footer())
        return root

    # -------- Keyboard thread --------
    def _keyboard_thread(self):
        def on_press(event):
            if event.event_type == keyboard.KEY_DOWN and event.name:
                try:
                    self.loop.call_soon_threadsafe(self.key_queue.put_nowait, event.name)
                except RuntimeError:
                    pass
        keyboard.hook(on_press)
        keyboard.wait()

    # -------- Orchestration logic --------
    def _set_msg(self, msg: str):
        self.last_message = msg
        self.live.update(self.render(), refresh=True)

    async def _ui_heartbeat(self, interval: float = 1.0):
        """Rafraîchit périodiquement l'interface toutes les X secondes."""
        while True:
            try:
                self.live.update(self.render(), refresh=True)
                await asyncio.sleep(interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                # Si jamais une erreur survient, on logge et continue
                from datetime import datetime
                print(f"[{datetime.now():%H:%M:%S}] [HEARTBEAT ERROR] {e}")
                await asyncio.sleep(interval)

    async def run(self):
        # Lancer thread clavier
        t = threading.Thread(target=self._keyboard_thread, daemon=True)
        t.start()

        # Connexion robot au démarrage
        self._set_msg(f"Connexion au robot {ROBOT_IP}…")
        try:
            await self.robot.connect()
            if self.robot.connected:
                self._set_msg("Robot connecté.")
            else:
                self._set_msg("Robot non connecté.")
        except Exception as e:
            self._set_msg(f"Échec connexion: {e}")

        self._ui_heartbeat_task = asyncio.create_task(self._ui_heartbeat(1))

        # Boucle principale
        while True:
            key = await self.key_queue.get()

            if key == "esc":
                await self.cancel_current()
                self._set_msg("Arrêt demandé.")
                break

            if key.lower() == "s":
                self._set_msg("État rafraîchi.")
                continue

            if key == "space":
                await self.cancel_current()
                continue

            if key in ACTIONS:
                await self.launch(key)
            # touches non gérées ignorées

    async def launch(self, key: str):
        if self.current_task and not self.current_task.done():
            self._set_msg(f"Déjà en cours: {self.current_name}. (Espace pour annuler)")
            return

        func = ACTIONS[key]
        name = func.__name__

        async def wrapper():
            try:
                self.current_name = name
                self.live.update(self.render(), refresh=True)
                await func(self.robot.robot)
                self._set_msg(f"{name} terminé.")
            except asyncio.CancelledError:
                self._set_msg(f"{name} annulé.")
                raise
            finally:
                self.current_task = None
                self.current_name = None
                self.live.update(self.render(), refresh=True)

        self._set_msg(f"Démarrage de {name}…")
        self.current_task = asyncio.create_task(wrapper())
        self.live.update(self.render(), refresh=True)

    async def cancel_current(self):
        if self.current_task and not self.current_task.done():
            self._set_msg(f"Annulation de {self.current_name}…")
            self.current_task.cancel()
            try:
                await self.current_task
            except asyncio.CancelledError:
                pass
        else:
            self._set_msg("Aucune action en cours.")
        self.live.update(self.render(), refresh=True)

# =========================
#  Entrée du programme
# =========================
def main():
    # NOTE Windows: `keyboard` peut nécessiter de lancer le script en administrateur.
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    robot_mgr = RobotManager(ROBOT_IP, API_KEY)

    with Live(refresh_per_second=10, screen=True) as live:
        orch = Orchestrator(loop, live, robot_mgr)
        live.update(orch.render(), refresh=True)
        try:
            loop.run_until_complete(orch.run())
        finally:
            loop.stop()
            loop.close()

if __name__ == "__main__":
    main()
