from datetime import datetime

import sqlalchemy as sa

from comment_tree.postgres.tables import comment_table


def insert_comment(
    user_login: str,
    post_id: int,
    reply_to_comment_id: int | None,
    content: str,
    timestamp: datetime,
):
    return sa.insert(comment_table).values(
        user_login=user_login,
        post_id=post_id,
        reply_to_comment_id=reply_to_comment_id,
        content=content,
        timestamp=timestamp,
    )


def delete_comment(comment_id: int, user_login: str):
    return sa.delete(comment_table).where(
        sa.and_(
            comment_table.c.user_login == user_login,
            comment_table.c.id == comment_id,
        )
    )


def update_comment(comment_id: int, content: str, user_login: str):
    return (
        sa.update(comment_table)
        .where(
            sa.and_(
                comment_table.c.user_login == user_login,
                comment_table.c.id == comment_id,
            )
        )
        .values(content=content)
    )


def select_comments_under_posts(post_ids: list[int]):
    return sa.select(comment_table).where(comment_table.c.post_id.in_(post_ids))
