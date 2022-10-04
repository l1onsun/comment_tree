import functools
from dataclasses import dataclass
from datetime import datetime
from typing import Callable

from sqlalchemy.ext.asyncio import AsyncEngine

from comment_tree.authorization.password_hash import hash_password
from comment_tree.postgres.db_models import DbComment, DbPost, DbUserPassword
from comment_tree.postgres.sql import comments_sql, posts_sql, users_sql
from comment_tree.postgres.tables import metadata

RECENT_POSTS_COUNT = 10


def engine_execute(storage_method: Callable):
    @functools.wraps(storage_method)
    async def wrapped(self: "Storage", *args, **kwargs):
        await self._execute(storage_method(self, *args, **kwargs))

    return wrapped


@dataclass
class Storage:
    engine: AsyncEngine

    async def _execute(self, statement):
        async with self.engine.begin() as conn:
            await conn.execute(statement)

    async def insert_user(self, login: str, password: str, fullname: str):
        await self._execute(
            users_sql.insert_user(
                login, hash_password(password), fullname, datetime.utcnow()
            )
        )

    async def insert_post(
        self,
        user_login: str,
        content: str,
    ):
        await self._execute(
            posts_sql.insert_post(user_login, content, datetime.utcnow())
        )

    async def insert_comment(
        self,
        user_login: str,
        post_id: int,
        reply_to_comment_id: int | None,
        content: str,
    ):
        await self._execute(
            comments_sql.insert_comment(
                user_login,
                post_id,
                reply_to_comment_id,
                content,
                timestamp=datetime.utcnow(),
            )
        )

    async def delete_post(self, post_id: int, user_login: str):
        await self._execute(posts_sql.delete_post(post_id, user_login))

    async def delete_comment(self, comment_id: int, user_login: str):
        await self._execute(comments_sql.delete_comment(comment_id, user_login))

    async def update_post(self, post_id: int, content: str, user_login: str):
        await self._execute(posts_sql.update_post(post_id, content, user_login))

    async def update_comment(self, comment_id: int, content: str, user_login: str):
        await self._execute(
            comments_sql.update_comment(comment_id, content, user_login)
        )

    async def select_user_by_login(self, login: str) -> DbUserPassword:
        async with self.engine.begin() as conn:
            return DbUserPassword.from_orm(
                (await conn.execute(users_sql.select_user_by_login(login))).one()
            )

    async def select_recent_posts(self) -> list[DbPost]:
        async with self.engine.begin() as conn:
            return [
                DbPost.from_orm(row)
                for row in (
                    await conn.execute(posts_sql.select_recent_posts())
                ).fetchmany(RECENT_POSTS_COUNT)
            ]

    async def select_comments_by_post_ids(self, post_ids: list[int]) -> list[DbComment]:
        async with self.engine.begin() as conn:
            return [
                DbComment.from_orm(row)
                for row in (
                    await conn.execute(
                        comments_sql.select_comments_under_posts(post_ids)
                    )
                ).fetchall()
            ]

    async def select_user_posts(self, user_login: str):
        async with self.engine.begin() as conn:
            return [
                DbPost.from_orm(row)
                for row in (
                    await conn.execute(posts_sql.select_user_posts(user_login))
                ).fetchall()
            ]

    async def create_all(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(metadata.create_all)
