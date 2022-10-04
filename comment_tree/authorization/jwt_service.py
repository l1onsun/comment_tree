from dataclasses import dataclass
from datetime import datetime, timedelta

from cfgv import ValidationError
from jose import JWTError, jwt
from pydantic import BaseModel

from comment_tree.exceptions import BaseApiException

ALGORITHM = "HS256"


@dataclass
class JwtService:
    jwt_secret_key: str

    def create_jwt_access_token(self, user_login: str):
        return jwt.encode(
            AccessToken.new(user_login).dict(),
            self.jwt_secret_key,
            algorithm=ALGORITHM,
        )

    def authorize_access_token(self, jwt_access_token: str) -> "AccessToken":
        try:
            token = self._parse_access_token(jwt_access_token)
        except JWTError | ValidationError:
            raise BaseApiException("Incorrect jwt-token")
        token.raise_exception_if_expired()
        return token

    def _parse_access_token(self, jwt_access_token: str) -> "AccessToken":
        return AccessToken(**self._decode_token(jwt_access_token))

    def _decode_token(self, jwt_token: str) -> dict:
        return jwt.decode(jwt_token, self.jwt_secret_key, algorithms=ALGORITHM)


class AccessToken(BaseModel):
    user_login: str
    expires: float

    @classmethod
    def new(cls, user_login: str) -> "AccessToken":
        return cls(
            user_login=user_login,
            expires=(datetime.utcnow() + timedelta(minutes=10)).timestamp(),
        )

    def raise_exception_if_expired(self):
        if datetime.utcnow() > datetime.fromtimestamp(self.expires):
            raise BaseApiException("Access token expired")
