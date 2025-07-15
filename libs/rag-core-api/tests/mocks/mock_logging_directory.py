"""Creates a mock logging configuration file for testing purposes.

This module provides functionality to create a temporary logging configuration file
with predefined settings for testing. The configuration is written to the path
specified in the LOGGING_DIRECTORY environment variable.
"""

import os


def mock_logging_config():
    """Create a mock logging configuration file for testing purposes."""
    with open(os.environ["LOGGING_DIRECTORY"], "w") as f:
        logging_config = """
    version: 1
    disable_existing_loggers: False

    formatters:
      simple:
        format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    handlers:
      console:
        class: logging.StreamHandler
        formatter: simple
        level: DEBUG
        stream: ext://sys.stdout

    loggers:
      my_logger:
        level: DEBUG
        handlers: [console]
        propagate: no

    root:
      level: DEBUG
      handlers: [console]
    """
        f.write(logging_config)
