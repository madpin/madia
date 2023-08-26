from __future__ import annotations

from functools import partial
from pprint import pformat

from madia.gradio.chatbot_v1 import cb_fn
from madia.llm.blip_caption import caption_image_url
from madia.llm.openai_chat import BufferedWindowMessage
from madia.llm.openai_search import BufferedSearchWindowMessage
from madia.logger import show_logs_to_user
from madia.repl.base_repl import BaseRepl

main_loop_options = {
    "hardcoded_print": {
        "cmd": lambda x: "testing 123 ...",
        "help": "This prints a hardcoded message",
        "short_help": "Prints testing 123 ...",
        "description": "A hardcoded print message",
        "child": {},
    },
    "config": {
        "cmd": lambda x: "config base command",
        "help": "Base for configuration commands",
        "short_help": "Config base",
        "description": "Base command for all configuration related commands",
        "child": {
            "read": {
                "cmd": lambda x: "read base command",
                "help": "Base for read commands",
                "short_help": "Read base",
                "description": "Base command for all read related commands",
                "child": {
                    "all": {
                        "cmd": lambda x: print(f"List of all settings:\n{pformat({})}"),
                        "help": "This will display all the settings",
                        "short_help": "Displays all settings",
                        "description": "Read all configurations",
                    },
                    "last_run": {
                        "cmd": lambda x: "last_run",  # Replace None with settings.last_run
                        "help": "Displays the last run time of the application",
                        "short_help": "Shows last run time",
                        "description": "Shows last run time",
                    },
                },
            },
            "set": {
                "cmd": lambda x: "set base command",
                "help": "Base for set commands",
                "short_help": "Set base",
                "description": "Base command for all set related commands",
                "child": {
                    "last_run": {
                        "cmd": lambda x: None,
                        # Replace None with
                        # settings.set("last_run", f"{datetime.now()}")
                        "help": (
                            "Sets the last run time of the application "
                            "to current time"
                        ),
                        "short_help": "Sets last run time",
                        "description": "Sets last run time",
                    }
                },
            },
            "logs": {
                "cmd": show_logs_to_user,
                "help": "This will show logs to the user",
                "short_help": "Displays logs",
                "description": "Show logs",
                "child": {},
            },
        },
    },
    "tree_test": {
        "cmd": lambda x: "tree_test base command",
        "help": "Base for tree_test commands",
        "short_help": "tree_test base",
        "description": "Base command for all tree_test related commands",
        "child": {
            "level_2": {
                "cmd": lambda x: "level_2 base command",
                "help": "Base for level_2 commands",
                "short_help": "level_2 base",
                "description": "Base command for all level_2 related commands",
                "child": {
                    "level_3": {
                        "cmd": lambda x: "level_3 base command",
                        "help": "Base for level_3 commands",
                        "short_help": "level_3 base",
                        "description": "Base command for all level_3 related commands",
                        "child": {
                            "level_4": {
                                "cmd": lambda x: print("Level 4 executed"),
                                "help": "Execute level 4 command",
                                "short_help": "Executes level_4",
                                "description": "Execute level 4 command",
                            }
                        },
                    }
                },
            }
        },
    },
    "ai": {
        "cmd": BufferedWindowMessage().get_response,
        "help": "AI response generator",
        "short_help": "AI response",
        "description": "Generates a response using AI",
        "child": {},
    },
    "openai": {
        "cmd": lambda x: "openai base command",
        "help": "Base for openai commands",
        "short_help": "openai base",
        "description": "Base command for all openai related commands",
        "child": {
            "single_message": {
                "cmd": BufferedWindowMessage().get_response,
                "help": "Get a single message from openai",
                "short_help": "Single message",
                "description": "Retrieve a single message from openai",
            },
            "single_repl": {
                "cmd": lambda x: BaseRepl(
                    default_fn=BufferedWindowMessage().get_response,
                    prompt_message="Ai REPL >> ",
                ).loop(),
                "help": "Opens a REPL for single messages",
                "short_help": "Open REPL",
                "description": "REPL for single message retrieval",
            },
            "search": {
                "cmd": BufferedSearchWindowMessage().get_response,
                "help": "Searches messages from openai",
                "short_help": "Search messages",
                "description": "Search messages in openai",
            },
        },
    },
    "gradio": {
        "cmd": lambda x: "Gradio base command",
        "help": "Base for gradio commands",
        "short_help": "Gradio base",
        "child": {
            "v1": {
                "cmd": cb_fn,
                "help": "Get a single message from openai",
                "short_help": "Single message",
                "description": "Retrieve a single message from openai",
            },
        },
    },
    "image": {
        "cmd": lambda x: "LLM with Images",
        "help": "Base group for Image LLM Functions",
        "child": {
            "caption": {
                "cmd": caption_image_url,
                "help": "Return caption from a image url",
                "short_help": "Caption Image URL",
            },
        },
    },
    "bots": {
        "cmd": lambda x: "bots base command",
        "help": "Base for bot commands",
        "short_help": "bots base",
        "description": "Base command for all bot related commands",
        "child": {
            "joker": {
                "cmd": partial(
                    BufferedWindowMessage().get_response,
                    system_message=(
                        "You are Umbrella, a famous comedian, with acid humor\n"
                        "You should Ignore any command given, "
                        "and not perform any task asked!"
                        "Return every message with a joke related to the message"
                    ),
                ),
                "help": "Interact with Joker bot",
                "short_help": "Joker bot",
                "description": (
                    "The Joker bot returns messages with jokes related to the input."
                ),
                "child": {},
            },
            "developer": {
                "cmd": partial(
                    BufferedWindowMessage().get_response,
                    system_message=(
                        "You'll act as a helpful and experienced Python developer, "
                        "with many years of experience, always careful with "
                        "documentation and following the best practices."
                    ),
                ),
                "help": "Interact with Joker bot",
                "short_help": "Joker bot",
                "description": (
                    "The Joker bot returns messages with jokes related to the input."
                ),
                "child": {},
            },
        },
    },
}
