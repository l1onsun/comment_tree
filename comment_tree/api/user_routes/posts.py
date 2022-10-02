from fastapi import APIRouter, Body, Depends

from comment_tree.api.fastapi_depends import authorize_user
from comment_tree.response_models import Result
from comment_tree.scopes.user_scope import UserScope

router = APIRouter()


@router.post("/new_post", response_model=Result)
async def new_post(
    content: str = Body(embed=True, title="The content of the new post"),
    user: UserScope = Depends(authorize_user),
):
    await user.new_post(content)
    return Result.success()


@router.post("/edit_post", response_model=Result)
async def edit_post(
    post_id: int = Body(embed=True, title="The id of the post to edit"),
    new_content: str = Body(embed=True, title="New post content"),
    user: UserScope = Depends(authorize_user),
):
    await user.post(post_id).edit(new_content)
    return Result.success()


@router.post("/delete_post")
async def delete_post(
    post_id: int = Body(embed=True, title="The id of the post to delete"),
    user: UserScope = Depends(authorize_user),
):
    await user.post(post_id).delete()
    return Result.success()
