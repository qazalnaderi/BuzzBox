from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.domain.models.admins import Admin
from app.services.auth_service.hash_service import HashService

hash_service = HashService()
async def verify_admin_credentials(db: AsyncSession, email_address: str, password: str):
    stmt = select(Admin).filter(Admin.email_address == email_address)
    result = await db.execute(stmt)
    admin = result.scalars().first()
    if not admin or not hash_service.verify_password(password, admin.password):
        return None
    return admin



async def get_admin_by_id(db: AsyncSession, admin_id: int) -> Admin:
    """Fetch admin from database by ID"""
    query = select(Admin).where(Admin.admin_id == admin_id)
    result = await db.execute(query)
    admin = result.scalar_one_or_none()
    return admin    