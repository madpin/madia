from __future__ import annotations

import os

from dynaconf import Dynaconf, loaders
from dynaconf.utils.boxing import DynaBox

# Constants in uppercase
SETTINGS_PATH = "~/.madia/config.yaml"
ABS_SETTINGS_PATH = os.path.expanduser(SETTINGS_PATH)
# Load settings from Dynaconf
settings = Dynaconf(
    settings_files=[ABS_SETTINGS_PATH],
    environments=True,  # Enable environment variable overrides
)


def save_settings():
    data = settings.as_dict(env="dev")

    # Get the absolute path and directory of the config file
    config_dir = os.path.dirname(ABS_SETTINGS_PATH)

    # Use a with statement to ensure proper handling of directory creation
    os.makedirs(config_dir, exist_ok=True)
    # Write settings to the config file
    loaders.write(
        ABS_SETTINGS_PATH,
        DynaBox(data).to_dict(),
        merge=False,
        env="dev",
    )


def check_settings():
    """Check if settings exist and load defaults if not"""
    default_settings = {
        "log_path": "~/.madia/logs",
        "rep_hist_path": "~/.madia/repl_history",
        "log_filename": "app.log",
        "log_filename_full_fp": "app_fp.log",
        "rep_hist": True,
    }

    new_key = False
    for key, value in default_settings.items():
        if not settings.get(key):
            if "path" in key and "~" in value:
                os.makedirs(os.path.expanduser(value), exist_ok=True)
            new_key = True
            settings[key] = value

    if new_key:
        save_settings()
