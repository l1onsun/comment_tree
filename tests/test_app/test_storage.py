import pytest

from comment_tree.postgres.storage import Storage


@pytest.mark.asyncio
@pytest.mark.integration
async def test_insert_select_user(storage: Storage):
    await storage.insert_user("user_login", "user_password", "fullname")
    user = await storage.select_user_by_login("user_login")
    assert user.user_login == "user_login"
    user.verify_password("user_password")
