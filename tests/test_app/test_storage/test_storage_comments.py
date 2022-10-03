import pytest
from sqlalchemy.exc import IntegrityError

from comment_tree.postgres.db_models import DbComment
from comment_tree.postgres.storage import Storage


def _as_set_of_tuples(comments: list[DbComment]):
    return {
        (
            comment.user_login,
            comment.post_id,
            comment.reply_to_comment_id,
            comment.content,
        )
        for comment in comments
    }


@pytest.mark.asyncio
@pytest.mark.integration
async def test_comment_should_have_user(storage: Storage):
    with pytest.raises(IntegrityError):
        await storage.insert_comment("user", 1, None, "comment")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_comment_should_have_parent_post(storage: Storage):
    await storage.insert_user("user", "password", "fullname")
    with pytest.raises(IntegrityError):
        await storage.insert_comment("user", 1, None, "comment")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_select_comments_by_post_ids(storage: Storage):
    await storage.insert_user("user", "password", "fullname")
    await storage.insert_post("user", "post 1")
    await storage.insert_comment("user", 1, None, "comment")
    await storage.insert_comment("user", 1, 1, "reply comment")
    await storage.insert_post("user", "post 2")
    await storage.insert_comment("user", 2, None, "other comment")

    db_comments = await storage.select_comments_by_post_ids([1])
    assert _as_set_of_tuples(db_comments) == {
        ("user", 1, None, "comment"),
        ("user", 1, 1, "reply comment"),
    }
