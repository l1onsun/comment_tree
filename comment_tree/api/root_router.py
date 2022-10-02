from fastapi import APIRouter

from comment_tree.api.guest_routes.auth import router as registration_router
from comment_tree.api.guest_routes.view import router as view_router
from comment_tree.api.user_routes.comments import router as comments_router
from comment_tree.api.user_routes.posts import router as posts_router

root_router = APIRouter()

root_router.include_router(posts_router)
root_router.include_router(comments_router)
root_router.include_router(registration_router)
root_router.include_router(view_router)
