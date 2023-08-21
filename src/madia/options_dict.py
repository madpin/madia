from __future__ import annotations

from functools import partial
from pprint import pformat

from madia.llm.openai_chat import BufferedWindowMessage
from madia.llm.openai_search import BufferedSearchWindowMessage
from madia.logger import show_logs_to_user
from madia.repl.base_repl import BaseRepl

main_loop_options = {
    "hardcoded_print": {
        "cmd": lambda x: "testing 123 ...",
        "name": "hardcoded_print",
        "help": "This prints a hardcoded message",
        "short_help": "Prints testing 123 ...",
        "alias": ["print_test"],
        "description": "A hardcoded print message",
        "child": {},
    },
    "config": {
        "cmd": lambda x: "config base command",
        "name": "config",
        "help": "Base for configuration commands",
        "short_help": "Config base",
        "alias": ["configuration"],
        "description": "Base command for all configuration related commands",
        "child": {
            "read": {
                "cmd": lambda x: "read base command",
                "name": "read",
                "help": "Base for read commands",
                "short_help": "Read base",
                "alias": ["read_base"],
                "description": "Base command for all read related commands",
                "child": {
                    "all": {
                        "cmd": lambda x: print(f"List of all settings:\n{pformat({})}"),
                        "name": "read_all",
                        "help": "This will display all the settings",
                        "short_help": "Displays all settings",
                        "alias": ["read_all_configs"],
                        "description": "Read all configurations",
                    },
                    "last_run": {
                        "cmd": lambda x: "last_run",  # Replace None with settings.last_run
                        "name": "last_run",
                        "help": "Displays the last run time of the application",
                        "short_help": "Shows last run time",
                        "alias": ["last_run_time"],
                        "description": "Shows last run time",
                    },
                },
            },
            "set": {
                "cmd": lambda x: "set base command",
                "name": "set",
                "help": "Base for set commands",
                "short_help": "Set base",
                "alias": ["set_base"],
                "description": "Base command for all set related commands",
                "child": {
                    "last_run": {
                        "cmd": lambda x: None,
                        # Replace None with
                        # settings.set("last_run", f"{datetime.now()}")
                        "name": "set_last_run",
                        "help": (
                            "Sets the last run time of the application "
                            "to current time"
                        ),
                        "short_help": "Sets last run time",
                        "alias": ["set_last_run_time"],
                        "description": "Sets last run time",
                    }
                },
            },
            "logs": {
                "cmd": show_logs_to_user,
                "name": "logs",
                "help": "This will show logs to the user",
                "short_help": "Displays logs",
                "alias": ["show_logs"],
                "description": "Show logs",
                "child": {},
            },
        },
    },
    "tree_test": {
        "cmd": lambda x: "tree_test base command",
        "name": "tree_test",
        "help": "Base for tree_test commands",
        "short_help": "tree_test base",
        "alias": ["tree_test_base"],
        "description": "Base command for all tree_test related commands",
        "child": {
            "level_2": {
                "cmd": lambda x: "level_2 base command",
                "name": "level_2",
                "help": "Base for level_2 commands",
                "short_help": "level_2 base",
                "alias": ["level_2_base"],
                "description": "Base command for all level_2 related commands",
                "child": {
                    "level_3": {
                        "cmd": lambda x: "level_3 base command",
                        "name": "level_3",
                        "help": "Base for level_3 commands",
                        "short_help": "level_3 base",
                        "alias": ["level_3_base"],
                        "description": "Base command for all level_3 related commands",
                        "child": {
                            "level_4": {
                                "cmd": lambda x: print("Level 4 executed"),
                                "name": "level_4",
                                "help": "Execute level 4 command",
                                "short_help": "Executes level_4",
                                "alias": ["level_4_execute"],
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
        "name": "ai",
        "help": "AI response generator",
        "short_help": "AI response",
        "alias": ["ai_response"],
        "description": "Generates a response using AI",
        "child": {},
    },
    "openai": {
        "cmd": lambda x: "openai base command",
        "name": "openai",
        "help": "Base for openai commands",
        "short_help": "openai base",
        "alias": ["openai_base"],
        "description": "Base command for all openai related commands",
        "child": {
            "single_message": {
                "cmd": BufferedWindowMessage().get_response,
                "name": "single_message",
                "help": "Get a single message from openai",
                "short_help": "Single message",
                "alias": ["one_message"],
                "description": "Retrieve a single message from openai",
            },
            "single_repl": {
                "cmd": lambda x: BaseRepl(
                    default_fn=BufferedWindowMessage().get_response,
                    prompt_message="Ai REPL >> ",
                ).loop(),
                "name": "single_repl",
                "help": "Opens a REPL for single messages",
                "short_help": "Open REPL",
                "alias": ["repl"],
                "description": "REPL for single message retrieval",
            },
            "search": {
                "cmd": BufferedSearchWindowMessage().get_response,
                "name": "search",
                "help": "Searches messages from openai",
                "short_help": "Search messages",
                "alias": ["search_messages"],
                "description": "Search messages in openai",
            },
        },
    },
    "bots": {
        "cmd": lambda x: "bots base command",
        "name": "bots",
        "help": "Base for bot commands",
        "short_help": "bots base",
        "alias": ["bots_base"],
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
                "name": "joker",
                "help": "Interact with Joker bot",
                "short_help": "Joker bot",
                "alias": ["joke_bot"],
                "description": (
                    "The Joker bot returns messages with jokes related to the input."
                ),
                "child": {},
            }
        },
    },
}
