from os import environ

import pytest
import pytest_asyncio
from _pytest.mark import Mark
from fastapi import FastAPI

from comment_tree.env import Env
from comment_tree.postgres.storage import Storage
from comment_tree.service_provider.fastapi_helpers import app_get_service_provider
from comment_tree.service_provider.service_provider import ServiceProvider
from comment_tree.service_provider.types import Service, ServiceClass
from tests.override_factories import test_factories


@pytest.fixture
def env():
    return Env(
        postgres_uri=environ.get(
            "TEST_POSTGRES_URI", "postgresql+asyncpg://localhost/comments_tree_test"
        ),
        jwt_secret_key="jwt_secret_key",
        debug=True,
    )


@pytest.fixture
def service_provider(request, env):
    mark: Mark | None = request.node.get_closest_marker("provider_override")
    override_services: dict[ServiceClass, Service] = mark.args[0] if mark else {}
    override_services[Env] = env
    return ServiceProvider(test_factories, services=override_services)


@pytest_asyncio.fixture
async def app(service_provider: ServiceProvider) -> FastAPI:
    app = await service_provider.solve(FastAPI)
    await app.router.startup()
    yield app
    await app.router.shutdown()


@pytest.fixture
def solved_service_provider(app: FastAPI) -> ServiceProvider:
    return app_get_service_provider(app)


@pytest_asyncio.fixture
async def storage(solved_service_provider: ServiceProvider) -> Storage:
    return solved_service_provider.provide(Storage)
