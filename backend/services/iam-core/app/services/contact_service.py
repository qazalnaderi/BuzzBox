from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from ..infrastructure.repositories.contacts_repository import (
    get_contact_by_email,
    get_contact_by_id,
    create_contact,
    delete_contact,
    get_contacts_by_email
)
from ..infrastructure.repositories.account_repository import get_account_by_email
from ..infrastructure.repositories.account_repository import get_account_by_user_id


class ContactService:
    async def add_contact(self, user_id: int, contact_email: str, db: AsyncSession):
        # Fetch the user's account by user_id
        account = await get_account_by_user_id(db, user_id)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found for the user")

        # Check if the provided email belongs to an existing user
        existing_user = await get_account_by_email(db, contact_email)
        if not existing_user:
            raise HTTPException(
                status_code=404, detail="The provided email address does not belong to any existing user"
            )

        # Check if the contact already exists
        existing_contact = await get_contact_by_email(db, account.account_id, contact_email)
        if existing_contact:
            raise HTTPException(status_code=400, detail="Contact already exists in your contact list")

        # Create a new contact
        contact = await create_contact(db, account.account_id, contact_email)
        return {"contact_email": contact.contact_email}


    async def delete_contact(self, user_id: int, contact_email: str, db: AsyncSession):
        # Fetch the user's account by user_id
        account = await get_account_by_user_id(db, user_id)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found for the user")

        # Fetch the contact by its email
        contact = await get_contact_by_email(db, account.account_id, contact_email)
        if not contact:
            raise HTTPException(status_code=404, detail="Contact not found")

        # Delete the contact
        await delete_contact(db, contact)
        return {"message": "Contact deleted successfully"}

    async def get_contacts(self, email: str, db: AsyncSession):
        # Fetch contacts associated with the account's email
        contacts = await get_contacts_by_email(db, email)
        if not contacts:
            raise HTTPException(status_code=404, detail="No contacts found for this email")
        # Return only contact emails
        return [{"contact_email": contact.contact_email} for contact in contacts]