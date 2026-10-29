"""Settings, memory notes and API key storage for Claude Hub.

Everything lives in claude_hub/data/, which is git-ignored so secrets never
reach the repository.
"""

import json
import os
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
SETTINGS_FILE = DATA_DIR / "settings.json"
MEMORY_FILE = DATA_DIR / "memory.json"
KEY_FILE = DATA_DIR / "api_key.txt"

MODELS = ["claude-haiku-5-5", "claude-sonnet-5-5", "claude-opus-5-5"]

DEFAULT_SETTINGS = {
    "model": "claude-haiku-5-5",
    "max_tokens": 1024,
    "system_prompt": "You are a helpful assistant.",
}


def _read_json(path, default):
    try:
        return json.loads(path.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def _write_json(path, data):
    DATA_DIR.mkdir(exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


def load_settings():
    return {**DEFAULT_SETTINGS, **_read_json(SETTINGS_FILE, {})}


def save_settings(settings):
    _write_json(SETTINGS_FILE, settings)


def load_memory():
    return _read_json(MEMORY_FILE, [])


def save_memory(notes):
    _write_json(MEMORY_FILE, notes)


def get_api_key():
    # An environment variable wins over the key saved from the admin panel.
    env_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if env_key:
        return env_key
    if KEY_FILE.exists():
        return KEY_FILE.read_text().strip()
    return ""


def set_api_key(key):
    DATA_DIR.mkdir(exist_ok=True)
    KEY_FILE.write_text(key.strip())
    KEY_FILE.chmod(0o600)


def build_system_prompt():
    """The system prompt plus every saved memory note."""
    settings = load_settings()
    notes = load_memory()
    prompt = settings["system_prompt"]
    if notes:
        prompt += "\n\nThings to remember about the user and their work:\n"
        prompt += "\n".join(f"- {note}" for note in notes)
    return prompt
