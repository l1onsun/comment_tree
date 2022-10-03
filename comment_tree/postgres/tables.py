from sqlalchemy import TIMESTAMP, Column, ForeignKey, Integer, MetaData, String, Table

metadata = MetaData()

user_table = Table(
    "user",
    metadata,
    Column("login", String, primary_key=True, nullable=False),
    Column("password_hash", String, nullable=False),
    Column("fullname", String, nullable=False),
    Column("timestamp", TIMESTAMP(timezone=True), nullable=False),
)

post_table = Table(
    "post",
    metadata,
    Column("id", Integer, primary_key=True, nullable=False),
    Column(
        "user_login", None, ForeignKey(user_table.c.login), index=True, nullable=False
    ),
    Column("content", String, nullable=False),
    Column("timestamp", TIMESTAMP(timezone=True), index=True, nullable=False),
)

comment_table = Table(
    "comment",
    metadata,
    Column("id", Integer, primary_key=True, nullable=False),
    Column("user_login", None, ForeignKey(user_table.c.login), nullable=False),
    Column("post_id", None, ForeignKey(post_table.c.id), index=True, nullable=False),
    Column("reply_to_comment_id", None, ForeignKey("comment.id"), nullable=True),
    Column("content", String, nullable=False),
    Column("timestamp", TIMESTAMP(timezone=True), nullable=False),
)
