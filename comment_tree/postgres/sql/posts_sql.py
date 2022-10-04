from datetime import datetime

import sqlalchemy as sa

from comment_tree.postgres.tables import post_table


def insert_post(user_login: str, content: str, timestamp: datetime):
    return sa.insert(post_table).values(
        user_login=user_login,
        content=content,
        timestamp=timestamp,
    )


def delete_post(post_id: int, user_login: str):
    return sa.delete(post_table).where(
        sa.and_(post_table.c.user_login == user_login, post_table.c.id == post_id)
    )


def update_post(post_id: int, content: str, user_login: str):
    return (
        sa.update(post_table)
        .where(
            sa.and_(
                post_table.c.user_login == user_login,
                post_table.c.id == post_id,
            )
        )
        .values(content=content)
    )


def select_recent_posts():
    return sa.select(post_table).order_by(sa.desc("timestamp"))


def select_user_posts(user_login: str):
    return (
        sa.select(post_table)
        .where(post_table.c.user_login == user_login)
        .order_by(sa.desc("timestamp"))
    )
