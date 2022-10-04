from fastapi import FastAPI

from comment_tree.asgi import create_app
from comment_tree.service_provider.fastapi_helpers import app_get_service_provider
from comment_tree.service_provider.service_provider import ServiceProvider


def test_solve_fastapi():
    app = create_app()
    assert type(app) is FastAPI
    assert type(app_get_service_provider(app)) is ServiceProvider
