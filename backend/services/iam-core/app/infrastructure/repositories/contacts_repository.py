from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Session
from app.domain.models import contacts, accounts


async def get_contact_by_email(db: AsyncSession, account_id: int, email: str):
    stmt = select(contacts.Contact).filter(contacts.Contact.owner_id == account_id, contacts.Contact.contact_email == email)
    result = await db.execute(stmt)
    return result.scalars().first()


async def get_contact_by_id(db: AsyncSession, contact_id: int):
    stmt = select(contacts.Contact).filter(contacts.Contact.contact_id == contact_id)
    result = await db.execute(stmt)
    return result.scalars().first()


async def create_contact(db: AsyncSession, account_id: int, contact_email: str):
    new_contact = contacts.Contact(
        owner_id=account_id,
        contact_email=contact_email
    )
    db.add(new_contact)
    await db.commit()
    await db.refresh(new_contact)
    return new_contact



async def delete_contact(db: AsyncSession, contact):
    await db.delete(contact)
    await db.commit()


async def get_contacts_by_email(db: AsyncSession, email: str):
    stmt = (
        select(contacts.Contact)
        .join(accounts.Account)
        .filter(accounts.Account.email_address == email)
    )
    result = await db.execute(stmt)
    return result.scalars().all()
