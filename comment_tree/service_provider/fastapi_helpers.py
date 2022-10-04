from typing import Type

from fastapi import Depends, FastAPI, Request

from comment_tree.service_provider.service_provider import ServiceProvider
from comment_tree.service_provider.types import Service, TService


def app_set_service_provider(app: FastAPI, service_provider: ServiceProvider):
    app.state.service_provider = service_provider


def app_get_service_provider(app: FastAPI) -> ServiceProvider:
    return app.state.service_provider


def get_service_provider(request: Request) -> ServiceProvider:
    return app_get_service_provider(request.app)


def provide(service_class: Type[TService]) -> TService:
    def fastapi_dependency(
        service_provider: ServiceProvider = Depends(get_service_provider),
    ) -> Service:
        return service_provider.provide(service_class)

    return Depends(fastapi_dependency)
