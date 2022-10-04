from datetime import datetime

import sqlalchemy as sa

from comment_tree.postgres.tables import user_table


def insert_user(login: str, password_hash: str, fullname: str, timestamp: datetime):
    return sa.insert(user_table).values(
        login=login,
        password_hash=password_hash,
        fullname=fullname,
        timestamp=timestamp,
    )


def select_user_by_login(login: str):
    return sa.select(user_table.c.login, user_table.c.password_hash).where(
        user_table.c.login == login
    )
