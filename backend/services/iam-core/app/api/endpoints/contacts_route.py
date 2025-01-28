from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.contact_service import ContactService
from app.services.auth_service.user_service import get_current_user
from app.core.db.database import get_db
from app.infrastructure.repositories.account_repository import get_account_by_user_id
contact_router = APIRouter()
contact_service = ContactService()


@contact_router.post("/add-contact")
async def add_contact(contact_email: str, user_id: int = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await contact_service.add_contact(user_id, contact_email, db)

#TODO make these ok
@contact_router.delete("/delete-contact")
async def delete_contact(
    contact_email: str,
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await contact_service.delete_contact(user_id, contact_email, db)

@contact_router.get("/get-contacts")
async def get_contacts(user_id: int = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    account = await get_account_by_user_id(db, user_id)
    contacts = await contact_service.get_contacts(account.email_address, db)
    if not contacts:
        raise HTTPException(status_code=404, detail="No contacts found for this email")
    return contacts