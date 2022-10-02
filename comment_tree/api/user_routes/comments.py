from fastapi import APIRouter, Body, Depends

from comment_tree.api.fastapi_depends import authorize_user
from comment_tree.response_models import Result
from comment_tree.scopes.user_scope import UserScope

router = APIRouter()


@router.post("/new_comment", response_model=Result)
async def new_comment(
    reply_to_comment_id: int
    | None = Body(embed=True, title="The id of the comment to attach the new comment"),
    post_id: int = Body(
        embed=True, title="The id of the post to which the comment will be attached"
    ),
    content: str = Body(embed=True, title="The content of new comment"),
    user: UserScope = Depends(authorize_user),
):
    await user.post(post_id).new_comment(content, reply_to_comment_id)
    return Result.success()


@router.post("/edit_comment", response_model=Result)
async def edit_comment(
    comment_id: int = Body(embed=True, title="The id of the comment to edit"),
    new_content: str = Body(embed=True, title="New comment content"),
    user: UserScope = Depends(authorize_user),
):
    await user.comment(comment_id).edit(new_content)
    return Result.success()


@router.post("/delete_comment", response_model=Result)
async def delete_comment(
    comment_id: int = Body(embed=True, title="The id of the comment to delete"),
    user: UserScope = Depends(authorize_user),
):
    await user.comment(comment_id).delete()
    return Result.success()
