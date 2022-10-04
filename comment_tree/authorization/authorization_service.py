from dataclasses import dataclass

from comment_tree.authorization.jwt_service import JwtService
from comment_tree.postgres.storage import Storage
from comment_tree.scopes.user_scope import UserScope


@dataclass
class AuthorizationService:
    storage: Storage
    jwt_token_service: JwtService

    async def login_with_password(self, login: str, password: str) -> UserScope:
        db_user = await self.storage.select_user_by_login(login)
        db_user.verify_password(password)
        return self._create_user_scope(db_user.user_login)

    def login_with_jwt_token(self, jwt_access_token: str) -> UserScope:
        access_token = self.jwt_token_service.authorize_access_token(jwt_access_token)
        return self._create_user_scope(access_token.user_login)

    def _create_user_scope(self, user_login: str) -> UserScope:
        return UserScope(user_login, self.jwt_token_service, self.storage)
