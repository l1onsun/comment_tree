import functools
from dataclasses import dataclass
from datetime import datetime
from typing import Callable

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncEngine

from comment_tree.authorization.password_hash import hash_password
from comment_tree.postgres.db_models import DbComment, DbPost, DbUserPassword
from comment_tree.postgres.tables import comment_table, metadata, post_table, user_table

RECENT_POSTS_COUNT = 10


def engine_execute(storage_method: Callable):
    @functools.wraps(storage_method)
    async def wrapped(self: "Storage", *args, **kwargs):
        await self._engine_execute(storage_method(self, *args, **kwargs))

    return wrapped


@dataclass
class Storage:
    engine: AsyncEngine

    async def _engine_execute(self, statement):
        async with self.engine.begin() as conn:
            await conn.execute(statement)

    @engine_execute
    def insert_user(self, login: str, password: str, fullname: str):
        return sa.insert(user_table).values(
            login=login,
            password_hash=hash_password(password),
            fullname=fullname,
            timestamp=datetime.utcnow(),
        )

    @engine_execute
    def insert_post(
        self,
        user_login: str,
        content: str,
    ):
        return sa.insert(post_table).values(
            user_login=user_login,
            content=content,
            timestamp=datetime.utcnow(),
        )

    @engine_execute
    def insert_comment(
        self,
        user_login: str,
        post_id: int,
        reply_to_comment_id: int | None,
        content: str,
    ):
        return sa.insert(comment_table).values(
            user_login=user_login,
            post_id=post_id,
            reply_to_comment_id=reply_to_comment_id,
            content=content,
            timestamp=datetime.utcnow(),
        )

    @engine_execute
    async def delete_post(self, post_id: int, user_login: str):
        return sa.delete(post_table).where(
            sa.and_(post_table.c.user_login == user_login, post_table.c.id == post_id)
        )

    @engine_execute
    async def delete_comment(self, comment_id: int, user_login: str):
        return sa.delete(comment_table).where(
            sa.and_(
                comment_table.c.user_login == user_login,
                comment_table.c.id == comment_id,
            )
        )

    @engine_execute
    async def update_post(self, post_id: int, content: str, user_login: str):
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

    @engine_execute
    def update_comment(self, comment_id: int, content: str, user_login: str):
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

    async def select_user_by_login(self, login: str) -> DbUserPassword:
        async with self.engine.begin() as conn:
            return DbUserPassword.from_orm(
                (
                    await conn.execute(
                        sa.select(user_table.c.login, user_table.c.password_hash).where(
                            user_table.c.login == login
                        )
                    )
                ).one()
            )

    async def select_recent_posts(self) -> list[DbPost]:
        async with self.engine.begin() as conn:
            return [
                DbPost.from_orm(row)
                for row in (
                    await conn.execute(
                        sa.select(post_table).order_by(sa.desc("timestamp"))
                    )
                ).fetchmany(RECENT_POSTS_COUNT)
            ]

    async def select_comments_by_post_ids(self, post_ids: list[int]) -> list[DbComment]:
        async with self.engine.begin() as conn:
            return [
                DbComment.from_orm(row)
                for row in (
                    await conn.execute(
                        sa.select(comment_table).where(
                            comment_table.c.post_id.in_(post_ids)
                        )
                    )
                ).fetchall()
            ]

    async def select_user_posts(self, user_login):
        async with self.engine.begin() as conn:
            return [
                DbPost.from_orm(row)
                for row in (
                    await conn.execute(
                        sa.select(post_table)
                        .where(post_table.c.user_login == user_login)
                        .order_by(sa.desc("timestamp"))
                    )
                ).fetchall()
            ]

    async def create_all(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(metadata.create_all)
