import httpx
import pytest

from tests.test_app.test_api.conftest import AuthedUserFactoryType


@pytest.mark.asyncio
@pytest.mark.integration
async def test_two_users_flow(authed_user_factory: AuthedUserFactoryType):
    async with (
        authed_user_factory("user_one") as user_one_client,
        authed_user_factory("user_two") as user_two_client,
    ):
        await user_one_client.post("/new_post", json={"content": "hi all!"})
        await user_two_client.post(
            "/new_comment", json={"content": "hi user_one!", "post_id": 1}
        )
        await user_two_client.post(
            "/new_comment", json={"content": "how are you?", "post_id": 1}
        )
        await user_one_client.post(
            "/new_comment",
            json={
                "content": "i am fine, thanks!",
                "post_id": 1,
                "reply_to_comment_id": 2,
            },
        )
        user_one_posts_resp: httpx.Response = await user_two_client.get(
            "/user_one/posts"
        )
    response_json = user_one_posts_resp.json()
    assert user_one_posts_resp.status_code == 200
    assert response_json == {
        "status": "success",
        "error_message": None,
        "result": [
            {
                "id": 1,
                "content": "hi all!",
                "user_login": "user_one",
                "childs": [
                    {
                        "id": 1,
                        "content": "hi user_one!",
                        "user_login": "user_two",
                        "childs": [],
                    },
                    {
                        "id": 2,
                        "content": "how are you?",
                        "user_login": "user_two",
                        "childs": [
                            {
                                "id": 3,
                                "content": "i am fine, thanks!",
                                "user_login": "user_one",
                                "childs": [],
                            }
                        ],
                    },
                ],
            }
        ],
    }
