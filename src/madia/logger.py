# logger.py
from __future__ import annotations

import logging
import os
from logging.handlers import MemoryHandler, RotatingFileHandler
from typing import Iterator

from madia.config import settings

LOG_FILENAME = os.path.expanduser(
    os.path.join(settings.log_path, settings.log_filename)
)
LOG_FILENAME_FULL_FP = os.path.expanduser(
    os.path.join(settings.log_path, settings.log_filename_full_fp)
)
FORMATTER = "%(asctime)s [%(levelname)s] [%(name)s:%(lineno)d] %(message)s - "
FORMATTER_FULL_FP = "%(asctime)s [%(levelname)s] [%(pathname)s:%(lineno)d] %(message)s"
os.makedirs(os.path.dirname(LOG_FILENAME), exist_ok=True)

# Basic setup
logging.basicConfig(
    level=logging.DEBUG,
    format=FORMATTER,
    filename=LOG_FILENAME,
    filemode="a",
)

# Create a rotating file handler that can keep backups
file_handler_full_fp = RotatingFileHandler(
    LOG_FILENAME_FULL_FP,
    maxBytes=5 * 1024 * 1024,
    backupCount=5,
)
file_handler_full_fp.setFormatter(logging.Formatter(FORMATTER_FULL_FP))
# Create a rotating file handler that can keep backups
file_handler = RotatingFileHandler(
    LOG_FILENAME, maxBytes=5 * 1024 * 1024, backupCount=5
)
file_handler.setFormatter(logging.Formatter(FORMATTER))

# Create a memory handler to buffer logs
memory_handler = MemoryHandler(capacity=1024 * 10, target=file_handler)
logging.getLogger().addHandler(memory_handler)
logging.getLogger().addHandler(file_handler_full_fp)

# Remove default handler to prevent log messages being shown on the console
logging.getLogger().removeHandler(logging.getLogger().handlers[0])


# Define a function to get the logger. This is what other modules will use.
def get_logger(name: str) -> logging.Logger:
    """
    Retrieve a logger instance with the specified name.

    Args:
        name (str): The name to associate with the logger.

    Returns:
        logging.Logger: The logger instance associated with the provided name.
    """
    return logging.getLogger(name)


def get_buffered_logs(memory_handler: logging.handlers.MemoryHandler) -> Iterator[str]:
    """
    Retrieve buffered log messages from the specified memory handler.

    Args:
        memory_handler (logging.handlers.MemoryHandler): The memory handler storing buffered logs.

    Yields:
        Iterator[str]: An iterator yielding formatted log messages from the memory handler.
    """
    for record in memory_handler.buffer:
        yield logging.getLogger().handlers[0].format(
            record
        )  # using the formatter to format the log


def show_logs_to_user(memory_handler=memory_handler):
    """
    Display both buffered logs and logs from file to the user.

    Args:
        memory_handler (logging.handlers.MemoryHandler, optional): The memory handler storing buffered logs.
            Defaults to the module's predefined memory_handler.
    """
    # Show buffered logs
    print("Buffered Logs:")
    for log in get_buffered_logs(memory_handler):
        print(log)

    # Show logs from file
    print("\nLogs from file:")
    with open(LOG_FILENAME) as log_file:
        print(log_file.read())


class LoggingMixin:
    """
    A mixin class for adding logging capabilities to other classes.

    Attributes:
        logger (logging.Logger): The logger instance associated with the class.
            The logger name is derived from the class's module and name.
    """

    @property
    def logger(self):
        """
        Retrieve the logger instance associated with the class.

        Returns:
            logging.Logger: The logger instance.
        """
        name = ".".join([self.__module__, self.__class__.__name__])
        return logging.getLogger(name)
