from sqlalchemy.ext.asyncio import AsyncSession
from ..domain.schemas.accounts_schema import AdminLogin, UserLogin, LoginResponse
from ..infrastructure.repositories import account_repository, admin_repository
from ..services.auth_service.auth_tokens import create_access_token

class LoginService:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def admin_login(self, login_data: AdminLogin):
        admin = await admin_repository.verify_admin_credentials(self.db, login_data.email_address, login_data.password)
        if not admin:
            return {"status_code": 400, "message": "Invalid email or password"}

        token_data = {"admin_id": admin.admin_id, "email_address": admin.email_address}
        access_token = create_access_token(data=token_data)

        return LoginResponse(access_token=access_token, token_type="bearer")

    async def user_login(self, login_data: UserLogin):
        user = await account_repository.verify_user_credentials(self.db, login_data.email_address, login_data.password)
        if not user:
            return {"status_code": 400, "message": "User not found"}

        token_data = {"user_id": user.user_id, "email": user.email_address}
        access_token = create_access_token(data=token_data)

        return LoginResponse(access_token=access_token, token_type="bearer")
