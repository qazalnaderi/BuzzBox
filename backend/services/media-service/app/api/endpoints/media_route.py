from typing import Annotated, List
from loguru import logger
from fastapi import APIRouter, Depends, UploadFile, status, HTTPException
from fastapi.responses import StreamingResponse
from bson import ObjectId
from app.domain.schemas.media_schema import MediaSchema
from app.domain.schemas.token_schema import TokenDataSchema
from app.services.media_service import MediaService
from app.services.auth_service import get_current_user
from app.vaildators.vaildator import validate_image_file
from app.services.account_service import AccountService
from app.services.communication_service import CommunicationService
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.postgres_db.postgres_database import get_db
from fastapi import status
import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]  
)
import io
import zipfile
import asyncio
# from app.core.queue.queue_manager import queue_manager

from typing import Union, AsyncGenerator
logger = logging.getLogger(__name__)

media_router = APIRouter()



@media_router.get(
    "/get_user_profile/{account_email_address}",
    response_class=StreamingResponse,
    status_code=status.HTTP_200_OK
    )
async def get_user_profile(
    account_email_address: str,
    media_service: Annotated[MediaService, Depends()],
    account_service: Annotated[AccountService, Depends()],
    current_user: Annotated[TokenDataSchema, Depends(get_current_user)]
):
    user_response = await account_service.get_account_profile(account_email_address)
    logger.info(f"Account profile retrieved: {user_response}")

    if not user_response:
        logger.error(f"Account not found")
        raise HTTPException(
            status_code=404,
            detail=f"Account not found"
        )

    if not user_response.image_url:
        raise HTTPException(
            status_code=404,
            detail="No profile picture found for the specified user"
        )

    try:
        media_id = ObjectId(user_response.image_url)
        logger.info(f"Media id : {media_id}")
    except Exception as e:
        logger.error(f"Invalid media id format for user {account_email_address}: {e}")
        raise HTTPException(status_code=400, detail="Invalid media id format")

    media_schema, file_stream = await media_service.get_media(media_id, account_email_address)

    logger.info(f"Retrieving media file {media_schema.filename}")

    return StreamingResponse(
        content=file_stream(),
        media_type=media_schema.content_type,
        headers={
            "Content-Disposition": f"attachment; filename={media_schema.filename}"
        },
    )

@media_router.put(
    "/profile/upload",
    response_model=MediaSchema,
    status_code=status.HTTP_201_CREATED
)
async def upload_profile_picture(
    media_service: Annotated[MediaService, Depends()],
    file: UploadFile,
    current_user: Annotated[TokenDataSchema, Depends(get_current_user)],
    account_service: Annotated[AccountService, Depends()]
    ):
    logger.info(f"Validating profile picture for account🔃: {current_user.email_address}")
    validate_image_file(file)
    
    logger.info(f"Uploading profile picture✅: {file.filename}")
    
    output = await media_service.create_media(
        file=file, 
        email_address=current_user.email_address  
    )
    
    await account_service.update_profile_picture(
        email_address=current_user.email_address,
        media_url=str(output.mongo_id)
    )
    
    return output



@media_router.post(
    "/email/attachments",
    response_model=MediaSchema,
    status_code=status.HTTP_201_CREATED
)
async def upload_email_attachments(
    db: Annotated[AsyncSession, Depends(get_db)],
    media_service: Annotated[MediaService, Depends()],
    files: list[UploadFile],
    email_id:int,
    current_user: Annotated[TokenDataSchema, Depends(get_current_user)],
    communication: Annotated[CommunicationService, Depends()],
):
    try:
        attachment_urls = []
        
        if not files:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No files provided"
            )

        recp = await communication.get_email_receiver(db, email_id)
        if not recp:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No recipient found for email ID {email_id}"
            )


        for file in files:
            logger.info(f"Validating email attachment 🔃: {file.filename}")
            validate_image_file(file)

            logger.info(f"Uploading email attachment✅: {file.filename}")

            output_sender = await media_service.create_media(
                file=file,
                email_address=current_user.email_address,
            )
           
            
            output_receiver = await media_service.create_media(
                file=file,
                email_address=recp. recipient_email,
            )            

            result = await communication.upload_attachments(
                db=db,  
                email_id=email_id, 
                attachment_urls=[str(output_sender.mongo_id)]  
            )    
            attachment_urls.append(str(output_sender.mongo_id))

            last_output = output_sender

        logger.info(f"attachment_urls: {attachment_urls}")
        return last_output


    except HTTPException as e:
        logger.error(f"Failed to upload email attachments: {str(e)}")
        raise e
    except Exception as e:
        logger.error(f"Failed to upload email attachments: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload attachments: {str(e)}"
        )


@media_router.get(
    "/email/attachments/{email_id}",
    response_class=StreamingResponse,
    status_code=status.HTTP_200_OK
)
async def get_email_attachments(
    email_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    media_service: Annotated[MediaService, Depends()],
    communication: Annotated[CommunicationService, Depends()],
    current_user: Annotated[TokenDataSchema, Depends(get_current_user)],
    account_service: Annotated[AccountService, Depends()]):


    try:
        # Validate email and permissions
        email_data = await communication.get_email_by_id(db, email_id)
        if not email_data:
            raise HTTPException(404, detail=f"Email with ID {email_id} not found")
        
        sender = await account_service.get_account_by_id(email_data.sender_id)
        receiver = await communication.get_email_receiver(db, email_id)
        if current_user.email_address not in [sender.email_address, receiver.recipient_email]:
            raise HTTPException(403, detail="Access denied")

        attachments = await communication.get_email_attachments(db, email_id)
        if not attachments:
            raise HTTPException(404, detail="No attachments found")

        # Create ZIP file in memory
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for attachment_url in attachments:
                try:
                    media_id = ObjectId(attachment_url)
                    media_schema, file_stream = await media_service.get_media(media_id, current_user.email_address)
                    
                    # Handle different types of streams
                    if callable(file_stream):
                        file_stream = file_stream()

                    # Now handle generator or file-like object
                    if hasattr(file_stream, '__iter__') or hasattr(file_stream, '__next__'):
                        # It's a generator - consume it
                        content = b''.join(chunk if isinstance(chunk, bytes) else 
                                         chunk.encode('utf-8') if isinstance(chunk, str) else 
                                         bytes(chunk) 
                                         for chunk in file_stream)
                    elif hasattr(file_stream, 'read'):
                        # It's a file-like object
                        content = file_stream.read()
                    else:
                        # Direct content
                        content = file_stream

                    # Ensure content is bytes
                    if isinstance(content, str):
                        content = content.encode('utf-8')
                    
                    # Write to zip
                    zip_file.writestr(media_schema.filename, content)
                    
                except Exception as e:
                    logger.error(f"Error processing attachment {attachment_url}: {str(e)}")
                    logger.exception("Full error details:")
                    continue

        # Prepare ZIP for streaming
        zip_buffer.seek(0)
        zip_size = zip_buffer.getbuffer().nbytes
        
        if zip_size == 0:
            raise HTTPException(500, detail="Failed to create zip file - no valid attachments processed")

        headers = {
            "Content-Disposition": f"attachment; filename=email_{email_id}_attachments.zip",
            "Content-Type": "application/zip",
            "Content-Length": str(zip_size)
        }

        return StreamingResponse(
            zip_buffer,
            media_type="application/zip",
            headers=headers
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(500, detail=str(e))