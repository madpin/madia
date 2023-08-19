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
        env="development",
    )
