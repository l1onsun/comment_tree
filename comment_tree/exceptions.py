from dataclasses import dataclass
from typing import ClassVar

from fastapi import FastAPI, Request
from starlette.responses import JSONResponse

from comment_tree.response_models import Result


@dataclass
class BaseApiException(Exception):
    status_code: ClassVar[int] = 500
    error_message: str


def add_exception_handler(app: FastAPI):
    @app.exception_handler(BaseApiException)
    def exception_handler(_: Request, exception: BaseApiException):
        return JSONResponse(
            status_code=exception.status_code,
            content=Result.failure(exception.error_message),
        )
