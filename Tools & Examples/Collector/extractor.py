import json
from tqdm import tqdm
from pathlib import Path

# ======= CONFIG =======
INPUT_FILE = "runs/20251029_103631/semantic_memory.jsonl"  # fichier d'entrée (une ligne = snapshot JSON)
# =======================


def load_all_events(filepath: Path):
    """Charge toutes les lignes JSON et extrait les événements uniques."""
    events = []
    seen = set()
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in tqdm(lines, desc="Analyse du fichier", unit="ligne"):
        try:
            item = json.loads(line.strip())
            data_list = item["data"]["data"]
            for ev in data_list:
                key = json.dumps(ev, sort_keys=True)
                if key not in seen:
                    seen.add(key)
                    events.append(ev)
        except Exception as e:
            print(f"⚠️ Ligne ignorée (erreur: {e})")

    # tri chronologique
    events.sort(key=lambda x: x.get("hr_time", "00:00:00"))
    return events


def summarize_event(ev):
    """Retourne une ligne lisible avec emojis."""
    t = ev.get("hr_time", "??:??:??")
    typ = ev.get("type")

    if typ == "PerceptionEvent" and ev.get("perception_type") == "ASR":
        return f"[{t}] 👂 Robot heard: \"{ev.get('value')}\""
    elif typ == "TTSEvent":
        return f"[{t}] 🗣️ Robot said: \"{ev.get('value')}\""
    elif typ == "MissionEvent":
        name = ev.get("name", "unknown_function")
        return f"[{t}] ⚙️ Robot called function: {name}"
    else:
        return f"[{t}] 📦 Other event type: {typ}"


def main():
    path = Path(INPUT_FILE)
    if not path.exists():
        print(f"❌ Fichier introuvable : {path}")
        return

    events = load_all_events(path)
    all_types = sorted(set(e.get("type", "Unknown") for e in events))

    # --- Préparer sortie ---
    output_lines = []
    output_lines.append("=== 📜 TYPES D'ÉVÉNEMENTS DÉTECTÉS ===")
    for t in all_types:
        output_lines.append(f" - {t}")
    output_lines.append("")
    output_lines.append("=== 🕒 TIMELINE RECONSTITUÉE ===")
    for e in events:
        output_lines.append(summarize_event(e))

    # --- Sauvegarde ---
    out_path = path.with_suffix(".timeline.txt")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))

    print(f"\n✅ Analyse terminée. Résumé sauvegardé dans : {out_path}")
    print("\n".join(output_lines[:20]))  # aperçu des 20 premières lignes


if __name__ == "__main__":
    main()
