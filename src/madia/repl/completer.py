from functools import lru_cache
from madia.repl.utils import safe_shlex_split
from prompt_toolkit.completion import Completer, Completion
import shlex


class CustomCompleter(Completer):
    def __init__(self, completion_tree):
        super().__init__()
        self.completion_tree = completion_tree

    @lru_cache(maxsize=128)
    def _safe_shlex_split_cache(self, text):
        return safe_shlex_split(text)

    def get_completions(self, document, complete_event):
        # Convert the input text to lowercase for case-insensitive comparison.
        text = document.text_before_cursor.lower()

        # Parse the input text to extract arguments.
        arguments = self._safe_shlex_split_cache(text)

        if len(text) == 0 or text[-1] == " ":
            arguments.append("")

        # If there are no arguments or a space was just typed, suggest an empty option.
        if not arguments:
            yield Completion("", start_position=0)
            return

        # Traverse the completion tree based on parsed arguments.
        cur_tree = self.completion_tree
        for arg in arguments[:-1]:
            if callable(cur_tree):
                continue
            matching_key = next((k for k in cur_tree if k.lower() == arg), None)
            if isinstance(cur_tree, dict) and matching_key:
                cur_tree = cur_tree[matching_key]
            else:
                return

        # Get the prefix for suggestions at the current level.
        prefix = arguments[-1]

        # Check if the current level contains options (dict or list).
        if isinstance(cur_tree, dict):
            # Special handling for dictionary values that are lists
            matching_key = next((k for k in cur_tree if k.lower() == prefix), None)
            if matching_key and isinstance(cur_tree[matching_key], list):
                for option in cur_tree[matching_key]:
                    yield Completion(str(option), start_position=0)
                return

            # Regular handling for other dictionary values
            options = [o for o in cur_tree if str(o).lower().startswith(prefix)]
            for option in options:
                yield Completion(str(option), start_position=-len(prefix))

        elif isinstance(cur_tree, list):
            options = [o for o in cur_tree if str(o).lower().startswith(prefix)]
            for option in options:
                yield Completion(str(option), start_position=-len(prefix))
