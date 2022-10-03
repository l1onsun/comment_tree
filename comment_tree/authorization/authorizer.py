from dataclasses import dataclass
from datetime import datetime, timedelta

from jose import JWTError, jwt
from pydantic import BaseModel, ValidationError

from comment_tree.exceptions import BaseApiException
from comment_tree.postgres.storage import Storage
from comment_tree.scopes.guest_scope import GuestScope
from comment_tree.scopes.user_scope import UserScope

ALGORITHM = "HS256"
TOKEN_EXPIRES_FORMAT = "%Y-%m-%d %H:%M:%S.%f"


class AccessToken(BaseModel):
    user_login: str
    expires: float

    def raise_exception_if_expired(self):
        if datetime.utcnow() > datetime.fromtimestamp(self.expires):
            raise BaseApiException("Access token expired")


@dataclass
class Authorizer:
    storage: Storage
    jwt_secret_key: str

    def create_guest_scope(self) -> GuestScope:
        return GuestScope(self, self.storage)

    async def login_with_password(self, login: str, password: str) -> UserScope:
        db_user = await self.storage.select_user_by_login(login)
        db_user.verify_password(password)
        return self._create_user_scope(db_user.user_login)

    def login_with_jwt_token(self, jwt_access_token: str) -> UserScope:
        access_token = self._decode_access_token(jwt_access_token)
        access_token.raise_exception_if_expired()
        return self._create_user_scope(access_token.user_login)

    def create_jwt_access_token(self, user_login: str):
        return jwt.encode(
            AccessToken(
                user_login=user_login,
                expires=(datetime.utcnow() + timedelta(minutes=10)).timestamp(),
            ).dict(),
            self.jwt_secret_key,
            algorithm=ALGORITHM,
        )

    def _decode_access_token(self, jwt_access_token: str) -> AccessToken:
        try:
            return AccessToken(
                **jwt.decode(
                    jwt_access_token, self.jwt_secret_key, algorithms=ALGORITHM
                )
            )
        except JWTError | ValidationError:
            raise BaseApiException("Incorrect jwt-token")

    def _create_user_scope(self, user_login: str) -> UserScope:
        return UserScope(user_login, self, self.storage)
