from fastapi import FastAPI

from comment_tree.factories import factories
from comment_tree.service_provider.service_provider import ServiceProvider


def create_app(service_provider: ServiceProvider = None):
    service_provider = service_provider or ServiceProvider(factories)
    return service_provider.solve_sync(FastAPI)
