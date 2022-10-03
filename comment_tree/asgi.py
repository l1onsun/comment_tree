from fastapi import FastAPI

from comment_tree.factories import factories
from comment_tree.service_provider.service_provider import ServiceProvider


def app_factory():
    return ServiceProvider(factories).solve_sync(FastAPI)
