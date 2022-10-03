import pytest
from sqlalchemy.exc import IntegrityError

from comment_tree.postgres.db_models import DbPost
from comment_tree.postgres.storage import RECENT_POSTS_COUNT, Storage


def _as_set_of_tuples(posts: list[DbPost]):
    return {(post.user_login, post.content) for post in posts}


@pytest.mark.asyncio
@pytest.mark.integration
async def test_post_should_have_user(storage: Storage):
    with pytest.raises(IntegrityError):
        await storage.insert_post("guest", "i am not registered yet")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_posts_select_by_user(storage: Storage):
    await storage.insert_user("user_one", "user_password", "fullname")
    await storage.insert_user("user_two", "user_password", "fullname")
    await storage.insert_post("user_one", "post 1")
    await storage.insert_post("user_two", "post 2")
    await storage.insert_post("user_one", "post 3")

    user_one_posts = await storage.select_user_posts("user_one")
    assert _as_set_of_tuples(user_one_posts) == {
        ("user_one", "post 1"),
        ("user_one", "post 3"),
    }

    user_two_posts = await storage.select_user_posts("user_two")
    assert _as_set_of_tuples(user_two_posts) == {("user_two", "post 2")}


@pytest.mark.asyncio
@pytest.mark.integration
async def test_most_recent_posts(storage: Storage):
    await storage.insert_user("user", "user_password", "fullname")
    insert_posts_count = 20
    for i in range(insert_posts_count):
        await storage.insert_post("user", str(i))

    recent_posts = await storage.select_recent_posts()
    assert _as_set_of_tuples(recent_posts) == {
        ("user", str(i))
        for i in range(insert_posts_count - RECENT_POSTS_COUNT, insert_posts_count)
    }
