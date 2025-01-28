import logging
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from typing import List, Dict, Any
from app.domain.schemas.emails_schema import EmailModel
from ..infrastructure.repositories.email_repository import create_email, create_email_recipient
from ..infrastructure.repositories.smtp_repository import get_smtp_credentials_by_account_id
from ..infrastructure.repositories.account_repository import get_account_by_user_id, get_account_by_email
from app.infrastructure.repositories.email_repository import get_email_by_id, get_emails_by_sender, get_emails_for_recipient, get_recipient_by_email_id
from .mail_service import MailService
from app.domain.schemas.emails_schema import EmailCreate, EmailResponse, EmailRecipientResponse
from sqlalchemy.future import select
from app.domain.models.emails import Email, EmailRecipient
from sqlalchemy.ext.asyncio import AsyncSession

mail_service = MailService()

class CommunicationService:

    
    async def send_email(
        self,
        db: AsyncSession,
        user_id: int,
        recipient: str,
        subject: str,
        body: str,
      
    ) -> Dict[str, Any]:
        """
        Handle sending an email by creating it in the database, adding recipients,
        and sending it via SMTP with the sender's credentials.
        """
        account = await get_account_by_user_id(db, user_id)
        sender_id = account.account_id


        recipient_account = await get_account_by_email(db, recipient)
        if not recipient_account:
            raise HTTPException(
                status_code=404,
                detail="Recipient account does not exist"
            )
        
        if recipient_account.account_id == sender_id:
            raise HTTPException(
                status_code=400,
                detail="Cannot send email to yourself"
            )


        # Step 1: Fetch sender's SMTP credentials
        logging.info(f"Fetching SMTP credentials for sender ID: {sender_id}")
        smtp_credentials = await get_smtp_credentials_by_account_id(db, sender_id)
        if not smtp_credentials:
            raise HTTPException(status_code=404, detail="SMTP credentials not found for the sender")

        smtp_user = smtp_credentials.email_address
        smtp_pass = smtp_credentials.smtp_password

        # Step 2: Create the email in the database
        try:
            logging.info(f"Creating email record for sender: {smtp_user}")
            email_data = EmailCreate(sender_id=sender_id, subject=subject, body=body)
            email = await create_email(db, sender_id=email_data.sender_id, subject=email_data.subject, body=email_data.body)
        except Exception as e:
            logging.error(f"Failed to create email record: {e}")
            raise HTTPException(status_code=500, detail="Failed to create email record in the database")


        try:
            logging.info(f"Processing recipient: {recipient}")
            recipient = await create_email_recipient(db, email_id=email.email_id, recipient_email=recipient)

        except Exception as e:
                logging.error(f"Failed to create recipient record for {recipient}: {e}")
                raise HTTPException(status_code=500, detail=f"Failed to process recipient: {recipient}")
        
        # Step 4: Send the email via SMTP
        try:
            logging.info(f"Sending email via SMTP as: {smtp_user}")
            smtp_response = await mail_service.send_email_via_smtp(
                sender_email=smtp_user,
                recipient_email=recipient.recipient_email,
                subject=subject,
                body=body,
                smtp_user=smtp_user,
                smtp_pass=smtp_pass,
            )

            if smtp_response["status"] != "success":
                logging.error(f"SMTP error: {smtp_response['message']}")
                raise HTTPException(status_code=500, detail=f"SMTP error: {smtp_response['message']}")

        except Exception as e:
            logging.error(f"Failed to send email via SMTP: {e}")
            raise HTTPException(status_code=500, detail="Failed to send email via SMTP")

        logging.info(f"Email sent successfully: {email.email_id}")
        return {"message": "Email sent successfully"}


    
    async def fetch_emails_by_sender(self, sender_user_id: int, db: AsyncSession):

        sender_account = await get_account_by_user_id(db, sender_user_id)
        if not sender_account:
            raise HTTPException(
                status_code=404,
                detail=f"Sender account with user ID {sender_user_id} not found."
            )

        query = (
            select(Email, EmailRecipient)
            .join(EmailRecipient, Email.email_id == EmailRecipient.email_id)
            .where(Email.sender_id == sender_account.account_id)
        )
        
        result = await db.execute(query)
        rows = result.all()
        
        if not rows:
            return []
        
        emails_with_recipient = [
            {
                "email_id": email.email_id,
                "sender_id": email.sender_id,
                "subject": email.subject,
                "body": email.body,
                "created_at": email.created_at,
                "is_important": email.is_important,
                "recipient": recipient.recipient_email if recipient else None,  # Add null check
            }
            for email, recipient in rows
        ]
        
        logging.info(f"DEBUG: Final structured data: {emails_with_recipient}")
        
        return [EmailModel(**email) for email in emails_with_recipient]



    async def fetch_emails_for_recipient(self, recipient_user_id: int, db: AsyncSession):

        recipient_account = await get_account_by_user_id(db, recipient_user_id)
        if not recipient_account:
            raise HTTPException(status_code=404, detail=f"Recipient account not found")

        emails = await get_emails_for_recipient(db, recipient_account.email_address)
        if not emails:
            raise HTTPException(status_code=404, detail=f"No emails found for recipient with user ID {recipient_account.email_address}.")
        
        email_with_sender_info = []
        for email in emails:
            sender_account = await get_account_by_user_id(db, email.sender_id)
            if not sender_account:
                raise HTTPException(status_code=404, detail=f"Sender account with ID {email.sender_id} not found.")
            
            email_data = {
                "email_id": email.email_id,
                "subject": email.subject,
                "body": email.body,
                "sender_email": sender_account.email_address,  
                "received_at": email.created_at,
                "created_at": email.created_at,  
                "is_important": email.is_important, 
            }
            email_with_sender_info.append(email_data)

        return email_with_sender_info


    async def get_email_details(self, db: AsyncSession, user_id: int, email_id: int):
        account = await get_account_by_user_id(db, user_id)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")

        email = await get_email_by_id(db, email_id)

        if not email:
            raise HTTPException(status_code=404, detail="Email not found")

        if email.sender_id != account.account_id:
            raise HTTPException(status_code=404, detail="You are not allowed to see this")    
        return email        