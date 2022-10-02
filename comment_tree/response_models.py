from enum import Enum
from typing import Generic, TypeVar

from pydantic import BaseModel

TResult = TypeVar("TResult")


class SuccessOrFailureEnum(Enum):
    success = "success"
    failure = "failure"


class Result(BaseModel, Generic[TResult]):
    result: TResult | None
    status: SuccessOrFailureEnum
    error_message: str | None = None

    @classmethod
    def success(cls, result: TResult = None):
        return cls(result=result, status=SuccessOrFailureEnum.success)

    @classmethod
    def failure(cls, error_message: str):
        return cls(
            result=None,
            status=SuccessOrFailureEnum.failure,
            error_message=error_message,
        )


class CommentView(BaseModel):
    id: int
    user_login: int
    content: str
    childs: list["CommentView"]


class PostView(BaseModel):
    id: int
    user_login: int
    content: str
    childs: list[CommentView]
