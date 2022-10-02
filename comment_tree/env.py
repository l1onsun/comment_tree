from pydantic import BaseSettings


class Env(BaseSettings):
    postgres_uri: str  # "postgresql+asyncpg://scott:tiger@localhost/test"
    debug: bool
    jwt_secret_key: str
