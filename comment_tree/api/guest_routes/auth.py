from fastapi import APIRouter, Body, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from comment_tree.api.fastapi_depends import TOKEN_URL, authorize_guest
from comment_tree.scopes.guest_scope import GuestScope
from comment_tree.scopes.user_scope import UserScope

router = APIRouter()


class Login(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/register", response_model=Login)
async def register(
    login: str = Body(embed=True, title="User login"),
    password: str = Body(embed=True, title="User password"),
    fullname: str = Body(default="", embed=True, title="User fullname"),
    guest: GuestScope = Depends(authorize_guest),
):
    user = await guest.register_user(login, password, fullname)
    return Login(access_token=user.create_jwt_access_token())


@router.post(f"/{TOKEN_URL}", response_model=Login)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    guest: GuestScope = Depends(authorize_guest),
):
    user: UserScope = await guest.login_with_password(
        form_data.username, form_data.password
    )
    return Login(access_token=user.create_jwt_access_token())
