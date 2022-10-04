"""First revision

Revision ID: 2cb5310b9cea
Revises:
Create Date: 2022-10-03 17:17:43.804728

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "2cb5310b9cea"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "user",
        sa.Column("login", sa.String(), nullable=False),
        sa.Column("password_hash", sa.String(), nullable=False),
        sa.Column("fullname", sa.String(), nullable=False),
        sa.Column("timestamp", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("login"),
    )
    op.create_table(
        "post",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_login", sa.String(), nullable=False),
        sa.Column("content", sa.String(), nullable=False),
        sa.Column("timestamp", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ("user_login",),
            ["user.login"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "comment",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_login", sa.String(), nullable=False),
        sa.Column("post_id", sa.Integer(), nullable=False),
        sa.Column("reply_to_comment_id", sa.Integer(), nullable=True),
        sa.Column("content", sa.String(), nullable=False),
        sa.Column("timestamp", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ("post_id",),
            ["post.id"],
        ),
        sa.ForeignKeyConstraint(
            ("reply_to_comment_id",),
            ["comment.id"],
        ),
        sa.ForeignKeyConstraint(
            ("user_login",),
            ["user.login"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("comment")
    op.drop_table("post")
    op.drop_table("user")
    # ### end Alembic commands ###
