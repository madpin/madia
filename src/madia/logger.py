# logger.py
from __future__ import annotations

import logging
import os
from logging.handlers import MemoryHandler, RotatingFileHandler

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
def get_logger(name):
    return logging.getLogger(name)


def get_buffered_logs(memory_handler):
    for record in memory_handler.buffer:
        yield logging.getLogger().handlers[0].format(
            record
        )  # using the formatter to format the log


def show_logs_to_user(memory_handler=memory_handler):
    # Show buffered logs
    print("Buffered Logs:")
    for log in get_buffered_logs(memory_handler):
        print(log)

    # Show logs from file
    print("\nLogs from file:")
    with open(LOG_FILENAME) as log_file:
        print(log_file.read())


class LoggingMixin:
    @property
    def logger(self):
        name = ".".join([self.__module__, self.__class__.__name__])
        return logging.getLogger(name)
