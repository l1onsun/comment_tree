import contextlib
from typing import AsyncContextManager, Callable, TypeAlias

import httpx
import pytest_asyncio
from fastapi import FastAPI

from comment_tree.authorization.authorizer import Authorizer
from comment_tree.postgres.storage import Storage

LOGGED_IN_USER_LOGIN = "logged_in_user"
LOGGED_IN_USER_PASSWORD = "logged_in_user_password"


@pytest_asyncio.fixture
async def guest_client(app: FastAPI) -> httpx.AsyncClient:
    async with httpx.AsyncClient(app=app, base_url="http://app_test") as client:
        yield client


AuthedUserFactoryType: TypeAlias = Callable[
    [str], AsyncContextManager[httpx.AsyncClient]
]


@pytest_asyncio.fixture
async def authed_user_factory(
    request, app: FastAPI, authorizer: Authorizer, storage: Storage
) -> AuthedUserFactoryType:
    @contextlib.asynccontextmanager
    async def factory(login: str, password: str = "password"):
        if request.node.get_closest_marker("integration"):
            await storage.insert_user(login, password, "fullname")

        jwt_token = authorizer._create_user_scope(login).create_jwt_access_token()

        async with httpx.AsyncClient(
            app=app, base_url="http://app_test", headers=auth_headers(jwt_token)
        ) as client:
            yield client

    return factory


def auth_headers(token: str):
    return {"Authorization": f"Bearer {token}"}
