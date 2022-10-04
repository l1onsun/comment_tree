from dataclasses import dataclass

from comment_tree.postgres.storage import Storage


@dataclass
class UserScope:
    user_login: str
    authorizer: "authorizer.Authorizer"  # type: ignore[name-defined]  # ToDo
    storage: Storage

    def post(self, post_id: int) -> "PostHandle":
        return PostHandle(self.user_login, post_id, self.storage)

    def comment(self, comment_id: int) -> "CommentHandle":
        return CommentHandle(self.user_login, comment_id, self.storage)

    async def new_post(self, content: str):
        await self.storage.insert_post(user_login=self.user_login, content=content)

    def create_jwt_access_token(self):
        return self.authorizer.create_jwt_access_token(self.user_login)


@dataclass
class PostHandle:
    user_login: str
    post_id: int
    storage: Storage

    async def new_comment(self, content: str, reply_to_comment_id: int | None):
        await self.storage.insert_comment(
            user_login=self.user_login,
            post_id=self.post_id,
            reply_to_comment_id=reply_to_comment_id,
            content=content,
        )

    async def delete(self):
        await self.storage.delete_post(self.post_id, self.user_login)

    async def edit(self, new_content: str):
        await self.storage.update_post(self.post_id, new_content, self.user_login)


@dataclass
class CommentHandle:
    user_login: str
    comment_id: int
    storage: Storage

    async def edit(self, new_content: str):
        await self.storage.update_comment(self.comment_id, new_content, self.user_login)

    async def delete(self):
        await self.storage.delete_comment(self.comment_id, self.user_login)
