from fastapi import APIRouter
from src.auth_users.views import router as auth_router
from src.family_member.view import router as family_member_router
from src.home_essential.view import router as home_essential_router
from src.home_essential.view import grocery_router
from src.grocery_home_essentials.view import router as grocery_home_essentials_router
from src.tasks.views import router as tasks_router
from src.reminders.views import router as reminders_router 
from src.file_upload.views import router as file_upload_router 
from src.rewards.views import router as rewards_router 
from src.screen_savers.views import router as screen_savers_router
from src.completed_task.view import router as completed_task_router
from src.family_member_points.view import router as family_member_points_router
from src.reward_request_redeem.view import router as reward_request_redeem_router
from src.admin_users.views import router as admin_users_router
from src.calender_tasks.view import router as calender_tasks_router
from src.photos.view import router as photos_router
from src.daily_quotes.view import router as daily_quotes_router

router = APIRouter()

# Unified authentication and user management
router.include_router(auth_router)


# Feature modules
router.include_router(family_member_router)
router.include_router(daily_quotes_router)
router.include_router(photos_router)
router.include_router(calender_tasks_router)
router.include_router(admin_users_router)
router.include_router(reward_request_redeem_router)
router.include_router(family_member_points_router)
router.include_router(completed_task_router)
router.include_router(home_essential_router)
router.include_router(grocery_router)
router.include_router(grocery_home_essentials_router)
router.include_router(tasks_router)
router.include_router(reminders_router)
router.include_router(file_upload_router)
router.include_router(rewards_router)
router.include_router(screen_savers_router)

