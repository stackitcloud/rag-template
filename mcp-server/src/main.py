import logging.config

import yaml
from settings.logging_settings import LoggingSettings

from dependency_container import DependencyContainer

with open(LoggingSettings().directory, "r") as stream:
    config = yaml.safe_load(stream)

logging.config.dictConfig(config)

container = DependencyContainer()

container.rag_mcp_server().run()
