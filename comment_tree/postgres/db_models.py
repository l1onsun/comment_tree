from datetime import datetime

from pydantic import BaseModel

from comment_tree.authorization.password_hash import verify_password
from comment_tree.exceptions import BaseApiException


class DbModel(BaseModel):
    class Config:
        orm_mode = True


class DbUserPassword(DbModel):
    user_login: str
    password_hash: str

    def verify_password(self, password: str):
        if not verify_password(password, self.password_hash):
            raise BaseApiException("Wrong password")


class DbPost(DbModel):
    id: int
    user_login: str
    content: str
    timestamp: datetime


class DbComment(DbModel):
    id: int
    user_login: str
    content: str
    timestamp: datetime
    post_id: int
    reply_to_comment_id: int
