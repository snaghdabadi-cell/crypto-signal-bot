import json
import os
from typing import Any, Dict


MEMORY_FILE = "last_signals.json"
ENTRY_CHANGE_THRESHOLD = 0.003
SCORE_CHANGE_THRESHOLD = 5


def load_last_signals() -> Dict[str, Dict[str, Any]]:
    if not os.path.exists(MEMORY_FILE):
        return {}

    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, dict):
            return {}

        return data

    except Exception as error:
        print(f"Could not load signal memory: {error}")
        return {}


def save_last_signals(signals: Dict[str, Dict[str, Any]]) -> None:
    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as file:
            json.dump(signals, file, ensure_ascii=False, indent=2)

    except Exception as error:
        print(f"Could not save signal memory: {error}")


def is_new_signal(symbol: str, signal: Dict[str, Any], old_signals: Dict[str, Dict[str, Any]]) -> bool:
    old_signal = old_signals.get(symbol)

    if old_signal is None:
        return True

    if old_signal.get("side") != signal.get("side"):
        return True

    old_score = float(old_signal.get("score", 0))
    new_score = float(signal.get("score", 0))

    if abs(new_score - old_score) >= SCORE_CHANGE_THRESHOLD:
        return True

    old_entry = float(old_signal.get("entry", 0))
    new_entry = float(signal.get("entry", 0))

    if old_entry <= 0 or new_entry <= 0:
        return True

    entry_change = abs(new_entry - old_entry) / old_entry

    if entry_change >= ENTRY_CHANGE_THRESHOLD:
        return True

    return False