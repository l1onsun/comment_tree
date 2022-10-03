from unittest.mock import AsyncMock, Mock

import httpx
import pytest

from comment_tree.factories import CreateTablesFlag
from comment_tree.postgres.storage import Storage
from tests.test_app.test_api.conftest import auth_headers


@pytest.mark.asyncio
@pytest.mark.provider_override({Storage: AsyncMock(), CreateTablesFlag: None})
async def test_registration(guest_client: httpx.AsyncClient, storage: AsyncMock):
    storage.select_user_by_login.return_value = (db_user := Mock())
    db_user.user_login = (login := "my_login")

    registration_response = await guest_client.post(
        "/register", json={"login": login, "password": "my_password"}
    )
    response_json = registration_response.json()
    token = response_json["access_token"]

    assert registration_response.status_code == 200
    assert response_json == {
        "access_token": token,
        "token_type": "bearer",
    }

    me_response = await guest_client.get("/me", headers=auth_headers(token))
    assert me_response.json() == {
        "status": "success",
        "result": login,
        "error_message": None,
    }
