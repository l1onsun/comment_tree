from fastapi import FastAPI

from comment_tree.factories import factories
from comment_tree.service_provider.service_provider import ServiceProvider


def create_app(service_provider: ServiceProvider = None):
    return (service_provider or ServiceProvider(factories)).solve_sync(FastAPI)
