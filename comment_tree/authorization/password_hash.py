from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(password_to_be_verified: str, hashed_password: str):
    return pwd_context.verify(password_to_be_verified, hashed_password)


def hash_password(password: str):
    return pwd_context.hash(password)
