"""Module for the main FastAPI application."""

# coding: utf-8

import logging.config

import yaml
from fastapi import FastAPI

from extractor_api_lib.apis.extractor_api import router
from extractor_api_lib.dependency_container import DependencyContainer
from extractor_api_lib.impl import extractor_api_impl

with open("/config/logging.yaml", "r") as stream:
    config = yaml.safe_load(stream)
logging.config.dictConfig(config)

app = FastAPI(
    title="extractor-api-lib",
    description="Extractor API lib",
    version="1.0.0",
)
container = DependencyContainer()
container.wire(modules=[extractor_api_impl])
app.container = container

app.include_router(router)


def register_dependency_container(new_container: DependencyContainer):
    """
    Register a new dependency container and rewire the application container.

    Parameters
    ----------
    new_container : DependencyContainer
        The new dependency container to be registered.

    Notes
    -----
    This function preserves the old wiring configuration and then overrides the
    application container with the new container. It rewires the application
    container to include modules from both the old and new wiring configurations.
    """
    # preserve old wiring
    wiring_target = container.wiring_config.modules
    app.container.override(new_container)

    # rewire
    wiring_target = list(set(wiring_target + new_container.wiring_config.modules))
    app.container.wire(modules=wiring_target)
