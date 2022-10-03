import httpx
import pytest_asyncio
from fastapi import FastAPI

from comment_tree.authorization.authorizer import Authorizer
from comment_tree.postgres.storage import Storage

LOGGED_IN_USER_LOGIN = "logged_in_user"
LOGGED_IN_USER_PASSWORD = "logged_in_user_password"


@pytest_asyncio.fixture
async def app_client(app: FastAPI) -> httpx.AsyncClient:
    async with httpx.AsyncClient(app=app, base_url="http://app_test") as client:
        yield client


@pytest_asyncio.fixture
async def app_client_with_auth(
    request, app: FastAPI, authorizer: Authorizer, storage: Storage
) -> httpx.AsyncClient:
    if request.node.get_closest_marker("integration"):
        storage.insert_user(LOGGED_IN_USER_LOGIN, LOGGED_IN_USER_PASSWORD, "fullname")

    token = authorizer._create_user_scope(
        LOGGED_IN_USER_LOGIN
    ).create_jwt_access_token()
    async with httpx.AsyncClient(
        app=app, base_url="http://app_test", headers=auth_headers(token)
    ) as client:
        yield client


def auth_headers(token: str):
    return {"Authorization": f"Bearer {token}"}
