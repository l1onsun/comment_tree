import sqlalchemy.ext.asyncio as sa
from fastapi import FastAPI

from comment_tree.api.root_router import root_router
from comment_tree.env import Env
from comment_tree.exceptions import add_exception_handler
from comment_tree.service_provider.service_factory import ServiceFactories
from comment_tree.service_provider.service_provider import ServiceProvider

factories = ServiceFactories()


@factories.add
def parse_env() -> Env:
    return Env()


@factories.add
def build_fastapi(service_provider: ServiceProvider) -> FastAPI:
    app = FastAPI(on_startup=[lambda: service_provider.solve_all()])
    app.service_provider = service_provider  # type: ignore
    app.include_router(root_router)
    add_exception_handler(app)

    return app


@factories.add
def build_postgres_engine(env: Env) -> sa.AsyncEngine:
    return sa.create_async_engine(
        env.postgres_uri,
        echo=env.debug,
        future=True,
    )


# @factories.add
# def build_postgres_engine(env: Env) -> sa.AsyncEngine:
#     return sa.create_async_engine(
#         env.postgres_uri,
#         echo=env.debug,
#     )
