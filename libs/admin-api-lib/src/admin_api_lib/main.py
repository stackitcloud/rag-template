"""Module for the main FastAPI application."""

# coding: utf-8

import logging.config
import yaml

from admin_api_lib.impl import admin_api
from fastapi import FastAPI
from rag_core_lib.impl.settings.rag_class_types_settings import RAGClassTypeSettings
from dependency_injector.containers import Container


from admin_api_lib.apis.admin_api import router
from admin_api_lib.dependency_container import DependencyContainer


with open("/config/logging.yaml", "r") as stream:
    config = yaml.safe_load(stream)
logging.config.dictConfig(config)

app = FastAPI(
    title="admin-api-lib",
    description="The API is used for the communication between the \
        admin frontend and the admin backend in the rag project.",
    version="1.0.0",
)
container = DependencyContainer()
container.class_selector_config.from_dict(RAGClassTypeSettings().model_dump())

app.container = container
container.wire(modules=[admin_api])
app.include_router(router)


def register_dependency_container(new_container: Container):
    """
    Register a new dependency container and rewire the application container.

    Parameters
    ----------
    new_container : Container
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
