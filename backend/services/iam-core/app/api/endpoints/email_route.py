import logging
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse
from app.services.communication_service import CommunicationService
from app.services.auth_service.user_service import get_current_user
from app.infrastructure.repositories.account_repository import get_account_by_user_id
from app.core.db.database import get_db
from app.domain.schemas.emails_schema import EmailSendRequest, EmailResponse, EmailModel,InboxResponse


email_router = APIRouter()
communication_service = CommunicationService()


@email_router.post("/send-email", status_code=status.HTTP_201_CREATED)
async def send_email(
    email_request: EmailSendRequest,
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        recipient = email_request.recipient
        subject = email_request.subject
        body = email_request.body
        
        logging.info(f"recipient, subject, body: {recipient, subject, body}")

        if not recipient:
            raise HTTPException(status_code=400, detail="Recipient field cannot be empty.")\

        
        response = await communication_service.send_email(
            db=db,
            user_id=user_id,
            recipient=recipient,
            subject=subject,
            body=body
        )

        return {
            "status_code": 201,
            "message": "Email sent successfully",
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"message": f"An unexpected error occurred: {str(e)}"},
        )


@email_router.get("/sent/{sender_id}", response_model=list[EmailModel])
async def get_sent_emails(
    user_id: int = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    try: 
        sent_emails = await communication_service.fetch_emails_by_sender(user_id, db)
        if not sent_emails:
            raise HTTPException(status_code=404, detail="No sent emails found")
        
        return sent_emails
    except Exception as e:
        logger.error(f"Error fetching sent emails: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="An error occurred while fetching sent emails")

@email_router.get("/inbox/{recipient_email}", response_model=list[InboxResponse])
async def get_inbox(
    user_id: int = Depends(get_current_user),  
    db: AsyncSession = Depends(get_db)
):
    inbox_emails = await communication_service.fetch_emails_for_recipient(user_id,db)
    if not inbox_emails:
        raise HTTPException(status_code=404, detail="No emails found in inbox")

    return inbox_emails


@email_router.delete("/delete/{email_id}", status_code=status.HTTP_200_OK)
async def delete_email_from_inbox(
    email_id: int,
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        email_to_delete = await communication_service.get_email_by_id_and_recipient(email_id, user_id, db)

        if not email_to_delete:
            raise HTTPException(status_code=404, detail="Email not found in inbox")

        await communication_service.delete_email_from_inbox(email_id, user_id, db)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Email successfully deleted from inbox"},
        )

    except Exception as e:
        logger.error(f"Error deleting email from inbox: {str(e)}", exc_info=True)
        return create_error_response(f"An error occurred while deleting the email: {str(e)}")


def get_communication_service():
    return CommunicationService()

@email_router.get("/emails/{email_id}")
async def get_email_by_id(
    email_id: int,
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    communication_service: CommunicationService = Depends(get_communication_service)
):
    try:
        email = await communication_service.get_email_details(db,user_id, email_id)
        return email
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")        