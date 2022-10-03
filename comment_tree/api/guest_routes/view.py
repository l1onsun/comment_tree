from fastapi import APIRouter, Depends

from comment_tree.api.fastapi_depends import authorize_guest
from comment_tree.response_models import PostView, Result
from comment_tree.scopes.guest_scope import GuestScope

router = APIRouter()


@router.get("/{user_login}/posts", response_model=Result[list[PostView]])
async def get_user_posts(
    user_login: str,
    guest: GuestScope = Depends(authorize_guest),
):
    return Result.success(await guest.user_posts_by_login(user_login))


@router.get("/recent_posts", response_model=Result[list[PostView]])
async def get_recent_posts(
    guest: GuestScope = Depends(authorize_guest),
):
    return Result.success(await guest.global_recent_posts())
