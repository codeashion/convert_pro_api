from fastapi import APIRouter
from src.admin_users.views import router as admin_users_router
from src.family_member.view import router as family_member_router
from src.home_essential.view import router as home_essential

router = APIRouter()

router.include_router(admin_users_router)
router.include_router(family_member_router)
router.include_router(home_essential)

