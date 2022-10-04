from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from comment_tree.scopes.guest_scope import GuestScope, GuestService
from comment_tree.scopes.user_scope import UserScope
from comment_tree.service_provider.fastapi_helpers import provide

TOKEN_URL = "token"

get_bearer_token = OAuth2PasswordBearer(tokenUrl=TOKEN_URL)


def authorize_guest(
    guest_service=provide(GuestService),
) -> GuestScope:
    return guest_service.new_guest()


def authorize_user(
    guest: GuestScope = Depends(authorize_guest),
    jwt_token: str = Depends(get_bearer_token),
) -> UserScope:
    return guest.login_with_jwt_token(jwt_token)
