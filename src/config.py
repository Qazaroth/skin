"""Config Manager - loads and saves user configuration"""

import json
import os

CONFIG_FILE = "config.json"

DEFAULTS = {
    "base_url": "http://localhost:3000/api",
}


def load() -> dict:
    if not os.path.exists(CONFIG_FILE):
        save(DEFAULTS.copy())
        return DEFAULTS.copy()
    try:
        with open(CONFIG_FILE, "r") as f:
            data = json.load(f)
        # Fill in any missing keys with defaults
        for k, v in DEFAULTS.items():
            data.setdefault(k, v)
        return data
    except (json.JSONDecodeError, OSError):
        return DEFAULTS.copy()


def save(cfg: dict):
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=2)