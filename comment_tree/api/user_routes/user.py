from fastapi import APIRouter, Depends

from comment_tree.api.fastapi_depends import authorize_user
from comment_tree.response_models import Result
from comment_tree.scopes.user_scope import UserScope

router = APIRouter()


@router.get("/me", response_model=Result[str])
async def new_post(
    user: UserScope = Depends(authorize_user),
):
    return Result.success(user.user_login)
