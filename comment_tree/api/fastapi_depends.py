from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from comment_tree.authorization.authorizer import Authorizer
from comment_tree.service_provider.fastapi_helpers import provide

TOKEN_URL = "token"

get_bearer_token = OAuth2PasswordBearer(tokenUrl=TOKEN_URL)


def authorize_user(
    authorizer=provide(Authorizer), jwt_token: str = Depends(get_bearer_token)
):
    return authorizer.login_with_jwt_token(jwt_token)


def authorize_guest():
    raise NotImplementedError()  # ToDo
