from typing import Annotated, List
from loguru import logger
from fastapi import Depends, HTTPException, status, Request
from app.core.config.config import get_settings, Settings
from app.domain.schemas.token_schema import TokenDataSchema
from app.infrastructure.clients.http_client import HTTPClient
from datetime import datetime, timezone, timedelta
from pydantic import ValidationError
import json 

class IAMClient:
    def __init__(
        self,
        http_client: Annotated[HTTPClient, Depends()],
        config: Settings = Depends(get_settings),
    ):
        self.config = config
        self.http_client = http_client

    async def validate_token(self, token: str) -> TokenDataSchema:
        headers = {"Authorization": f"Bearer {token}"}
        async with self.http_client as client:
            response = await client.get(
                f"{self.config.IAM_URL}/auth/Me", headers=headers
            )
            response.raise_for_status()
            data = response.json()
            logger.debug(f"Raw IAM response data: {data}")
            

            email_address = None
            if data.get('accounts') and len(data['accounts']) > 0:
                email_address = data['accounts'][0].get('email_address')


            token_data = {
                "user_id": data.get("user_id"),
                "email_address": email_address,  # Make sure this field exists in response
                "is_verified":True
            }
            
            logger.debug(f"Processed token data: {token_data}")
            try:
                return TokenDataSchema(**token_data)
            except ValidationError as e:
                logger.error(f"Validation error: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Error validating token data: {e}"
                )
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Error processing token data"
                )



    # async def send_email_attachments(self, attachment_urls: List[str], token: str) -> dict:
    #     try:
    #         if not attachment_urls:
    #             raise ValueError("No attachment URLs provided")

    #         headers = {
    #             "Authorization": f"Bearer {token}",
    #             "Content-Type": "application/json"
    #         }
    #         token_data = await self.validate_token(token)
        
    #     # Try with a more structured payload
    #         payload = {
    #         "email_data": {
    #             "recipient": token_data.email_address,
    #             "subject": "Attachment Upload",    
    #             "body": "Your attachments",        
    #             "attachments": attachment_urls,
    #         },
    #         "type": "attachment"
    #     }

    #     # Convert to JSON string with specific formatting
    #         json_str = json.dumps(payload, ensure_ascii=False)
        
    #         logger.debug(f"Sending request to IAM with payload: {json_str}")

    #         async with self.http_client as client:
    #             response = await client.post(
    #                 f"{self.config.IAM_URL}/emails/send-email",
    #                 data=payload,  # Using json parameter like in validate_token
    #                 headers=headers
    #             )
                
    #             # Log raw response for debugging
    #             response_data = response.json()
    #             logger.debug(f"Raw IAM response data: {response_data}")
                
    #             # Raise for non-200 status codes
    #             response.raise_for_status()
                
    #             return response_data

    #     except ValidationError as e:
    #         logger.error(f"Validation error: {e}")
    #         raise HTTPException(
    #             status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    #             detail=f"Invalid request format: {str(e)}"
    #         )
    #     except HTTPException as e:
    #         logger.error(f"HTTP error in send_email_attachments: {str(e)}")
    #         raise
    #     except Exception as e:
    #         logger.error(f"Unexpected error in send_email_attachments: {str(e)}")
    #         raise HTTPException(
    #             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #             detail=f"Failed to send email attachments: {str(e)}"
    #         )