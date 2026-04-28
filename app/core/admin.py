from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

from app.config import settings
from app.models.user import User
from app.models.plan import Plan
from app.models.block import DailyBlock
from app.models.writing import WritingEntry
from app.models.resource import Resource, ResourceCategory
from app.models.review import MonthlyReview


class AdminAuth(AuthenticationBackend):
    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("admin_token")
        return token == settings.admin_secret_key

    async def login(self, request: Request) -> bool:
        form = await request.form()
        username = form.get("username", "")
        password = form.get("password", "")
        if username == settings.superadmin_email and password == settings.superadmin_password:
            request.session["admin_token"] = settings.admin_secret_key
            return True
        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True


class UserAdmin(ModelView, model=User):
    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-users"
    column_list = [User.id, User.email, User.display_name, User.is_active, User.is_superadmin, User.created_at]
    column_searchable_list = [User.email, User.display_name]
    column_sortable_list = [User.id, User.email, User.created_at]
    column_details_exclude_list = [User.password_hash]
    can_create = False
    can_delete = True
    can_edit = True
    can_export = True


class PlanAdmin(ModelView, model=Plan):
    name = "Plan"
    name_plural = "Plans"
    icon = "fa-solid fa-map"
    column_list = [Plan.id, Plan.user_id, Plan.name, Plan.is_active, Plan.created_at]
    column_searchable_list = [Plan.name]
    column_sortable_list = [Plan.id, Plan.created_at]
    can_create = False
    can_edit = False


class BlockAdmin(ModelView, model=DailyBlock):
    name = "Daily Block"
    name_plural = "Daily Blocks"
    icon = "fa-solid fa-calendar-check"
    column_list = [DailyBlock.id, DailyBlock.user_id, DailyBlock.plan_id, DailyBlock.date, DailyBlock.type, DailyBlock.duration_minutes]
    column_sortable_list = [DailyBlock.id, DailyBlock.date, DailyBlock.duration_minutes]
    can_create = False
    can_edit = False


class WritingAdmin(ModelView, model=WritingEntry):
    name = "Writing Entry"
    name_plural = "Writing Entries"
    icon = "fa-solid fa-pen"
    column_list = [WritingEntry.id, WritingEntry.user_id, WritingEntry.date, WritingEntry.word_count, WritingEntry.active_time_minutes]
    column_sortable_list = [WritingEntry.id, WritingEntry.date, WritingEntry.word_count]
    can_create = False
    can_edit = False


class ResourceAdmin(ModelView, model=Resource):
    name = "Resource"
    name_plural = "Resources"
    icon = "fa-solid fa-link"
    column_list = [Resource.id, Resource.user_id, Resource.title, Resource.url, Resource.created_at]
    column_searchable_list = [Resource.title, Resource.url]
    can_create = False
    can_edit = False


class ReviewAdmin(ModelView, model=MonthlyReview):
    name = "Monthly Review"
    name_plural = "Monthly Reviews"
    icon = "fa-solid fa-chart-bar"
    column_list = [MonthlyReview.id, MonthlyReview.user_id, MonthlyReview.plan_id, MonthlyReview.month]
    can_create = False
    can_edit = False


def create_admin(app, engine) -> Admin:
    authentication_backend = AdminAuth(secret_key=settings.admin_secret_key)
    admin = Admin(app=app, engine=engine, authentication_backend=authentication_backend)
    admin.add_view(UserAdmin)
    admin.add_view(PlanAdmin)
    admin.add_view(BlockAdmin)
    admin.add_view(WritingAdmin)
    admin.add_view(ResourceAdmin)
    admin.add_view(ReviewAdmin)
    return admin
