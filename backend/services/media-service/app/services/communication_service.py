import logging
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from typing import List, Dict, Any
from app.infrastructure.repositories.attachment_repository import create_attachment
from app.infrastructure.repositories.email_repository import get_recipient_by_email_id, get_email_by_id, get_email_by_id, get_email_attachments
from loguru import logger
from fastapi import status



class CommunicationService:

    async def upload_attachments(self, db: AsyncSession, email_id: str, attachment_urls: list[str]):
        logger.info(f"Updating attachments for email: {email_id}")

        update_fields = {"attachment_urls": attachment_urls} 
        result = await create_attachment(db, email_id, update_fields)

        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update email attachments"
            )

        logger.info(f"Attachments for email {email_id} updated successfully.")
        return result

    async def get_email_attachments(self, db: AsyncSession, email_id: int):
        logger.info(f"Fetching attachment for email ID: {email_id}")
        attachments = await get_email_attachments(db, email_id)
        if not attachments:
            raise HTTPException(status_code=404, detail="No attachment not found")
        return attachments

    async def get_email_receiver(self, db:AsyncSession, email_id):
        email = await get_email_by_id(db, email_id) 
        if not email:
            raise HTTPException(status_code=404, detail="Email not found")
        recp = await get_recipient_by_email_id(db, email_id)
        if not recp:
            raise HTTPException(status_code=404, detail="Recepient not found") 
        return recp   

    async def get_email_by_id(self, db:AsyncSession, email_id):
        email = await get_email_by_id(db, email_id)
        return email