from fastapi import FastAPI

from comment_tree.asgi import app_factory
from comment_tree.service_provider.fastapi_helpers import app_get_service_provider
from comment_tree.service_provider.service_provider import ServiceProvider


def test_solve_fastapi():
    app = app_factory()
    assert type(app) is FastAPI
    assert type(app_get_service_provider(app)) is ServiceProvider
