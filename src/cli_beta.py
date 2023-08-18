# from prompt_toolkit import PromptSession
# from prompt_toolkit.completion import WordCompleter
# from prompt_toolkit.history import InMemoryHistory


# class REPL:
#     def __init__(self, completion_dict):
#         self.completion_words = self._extract_words(completion_dict)
#         self.session = PromptSession(
#             completer=WordCompleter(self.completion_words),
#             history=InMemoryHistory(),
#         )

#     @staticmethod
#     def _extract_words(completion_dict):
#         words = list(completion_dict.keys())
#         for key, value in completion_dict.items():
#             if isinstance(value, dict):
#                 words.extend(REPL._extract_words(value))
#             elif isinstance(value, list):
#                 words.extend(value)
#         return words

#     def loop(self):
#         while True:
#             try:
#                 command = self.session.prompt(">>> ")
#                 # Here, you can interpret the command and do something with it.
#                 # For this example, we'll just print it out.
#                 print(f"You entered: {command}")
#             except (EOFError, KeyboardInterrupt):
#                 print("Exiting REPL.")
#                 break


# if __name__ == "__main__":
#     main_loop_options = {
#         "config": {
#             "read": [],
#             "set": [],
#         },
#         "ai": "single_message",
#         "openai": "single_message",
#         "aichat": "chat_gpt_loop_mock",
#         "chatai": "chat_gpt_loop_mock",
#         "ai_search": "buffer_window_search_message_instance.get_response",
#         "ai_search2": "search_llmmath",
#     }

#     repl = REPL(main_loop_options)
#     repl.loop()
