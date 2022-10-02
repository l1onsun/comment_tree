import re
from dataclasses import dataclass, field

from comment_tree.api.guest_routes.view import PostView
from comment_tree.authorization.authorizer import Authorizer
from comment_tree.exceptions import BaseApiException
from comment_tree.postgres.db_models import DbComment, DbPost
from comment_tree.postgres.storage import Storage
from comment_tree.response_models import CommentView
from comment_tree.scopes.user_scope import UserScope

allowed_login_pattern = re.compile(r"^\w+$")


def raise_exception_if_login_not_allowed(login: str):
    if not allowed_login_pattern.match(login):
        raise BaseApiException("Login must contain only letters digits and underscores")


@dataclass
class GuestScope:
    authorizer: Authorizer
    storage: Storage

    async def register_user(self, login: str, password: str, fullname: str | None):
        raise_exception_if_login_not_allowed(login)
        await self.storage.insert_user(login, password, fullname)

    async def login_with_password(self, login: str, password: str):
        return self.authorizer.login_with_password(login, password)

    async def login_with_jwt_token(self, jwt_access_token: str) -> UserScope:
        return self.authorizer.login_with_jwt_token(jwt_access_token)

    async def user_posts_by_login(self, user_login: str) -> list[PostView]:
        posts = PostsHelper(await self.storage.select_user_posts(user_login))
        return await self._load_and_attach_comments(posts)

    async def global_recent_posts(self) -> list[PostView]:
        posts = PostsHelper(await self.storage.select_recent_posts())
        return await self._load_and_attach_comments(posts)

    async def _load_and_attach_comments(self, posts: "PostsHelper") -> list[PostView]:
        comments = await self._load_comments_under_posts(posts)
        return self._attach(posts, comments)

    async def _load_comments_under_posts(
        self, posts: "PostsHelper"
    ) -> "CommentsHelper":
        return CommentsHelper(
            await self.storage.select_comments_by_post_ids(posts.ids())
        )

    def _attach(
        self, posts: "PostsHelper", comments: "CommentsHelper"
    ) -> list[PostView]:
        for comment in comments.db_comments:
            posts.post_views[comment.post_id].childs.append(
                comments.comment_views[comment.id]
            )
        return list(posts.post_views.values())


@dataclass
class PostsHelper:
    db_posts: list[DbPost]
    post_views: dict[int, PostView] = field(init=False)

    def __post_init__(self):
        self.post_views = {
            post.id: PostView(childs=[], **post.dict()) for post in self.db_posts
        }

    def ids(self) -> list[int]:
        return list(self.post_views.keys())


@dataclass
class CommentsHelper:
    db_comments: list[DbComment]
    comment_views: dict[int, CommentView] = field(init=False)

    def __post_init__(self):
        self.comment_views: dict[int, CommentView] = {
            comment.id: CommentView(childs=[], **comment.dict())
            for comment in self.db_comments
        }
        self._attach_comments_to_comments()

    def _attach_comments_to_comments(self):
        for comment in self.db_comments:
            if comment.reply_to_comment_id:
                self.comment_views[comment.reply_to_comment_id].childs.append(
                    self.comment_views[comment.id]
                )
