import logging
from loguru import logger
import json
import traceback
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.repositories import account_repository
from app.domain.schemas.accounts_schema import UserCreate, AccountCreate, ResendOTPSchema
from app.helper import (
    suggest_email,
    convert_date_to_string,
    validate_email,
    validate_name,
    validate_gender,
    validate_phone_number,
    check_password_strength
)
from app.core.redis.redis_client import redis_client
from fastapi import HTTPException
from app.domain.schemas.accounts_schema import RegistrationResponse
from app.services.auth_service.otp_service import OTPService
from app.services.mail_service import MailService
from app.core.db.database import get_db
from fastapi import Depends
from app.helper import (
    OTPVerificationFailedError,
    MailboxCreationFailedError,
    UserCreationFailedError,
    AccountCreationFailedError,
    SMTPCredentialCreationFailedError  ,
    OTPResendFailedError  
)
import requests
from app.infrastructure.repositories import account_repository
from app.infrastructure.repositories import smtp_repository

from app.domain.schemas.accounts_schema import OTPCreate
mailservice = MailService()

otp_service = OTPService()

class RegistrationService:

    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db
        self.otp_service = OTPService()

    async def register_user(self, user_data: UserCreate, account_data: AccountCreate) -> RegistrationResponse:
        try:
            logging.info("Starting user registration process.")

            # Validation and error handling
            first_name_error = await validate_name(user_data.first_name)
            if first_name_error:
                return RegistrationResponse(message=first_name_error)

            last_name_error = await validate_name(user_data.last_name)
            if last_name_error:
                return RegistrationResponse(message=last_name_error)

            phone_number_error = await validate_phone_number(user_data.phone_number)
            if phone_number_error:
                return RegistrationResponse(message=phone_number_error)

            gender_error = await validate_gender(user_data.gender)
            if gender_error:
                return RegistrationResponse(message=gender_error)

            if await account_repository.get_user_by_phone(self.db, user_data.phone_number):
                return RegistrationResponse(message="Phone number already registered")

            email_validation_error = await validate_email(account_data.email_address)
            if email_validation_error:
                return RegistrationResponse(message=email_validation_error)

            password_error = await check_password_strength(account_data.password)
            if password_error:
                return RegistrationResponse(message=password_error)

            if account_data.recovery_email:
                recovery_email_error = await validate_email(account_data.recovery_email)
                if recovery_email_error:
                    return RegistrationResponse(message="Recovery email must end with @buzzbox.com")

                if not await account_repository.get_account_by_email(self.db, account_data.recovery_email):
                    return RegistrationResponse(message="Invalid recovery email")

            if await account_repository.get_account_by_email(self.db, account_data.email_address):
                suggested_email = await suggest_email(user_data.first_name, user_data.last_name)
                return RegistrationResponse(message=f"Email address already taken. Suggested: {suggested_email}")

            # Generate OTP and store in Redis
            otp = self.otp_service.generate_otp()
            logging.info(f"Generated OTP for email {account_data.email_address}: {otp}")
            redis_key = f"registration:{account_data.email_address.lower()}"
            temp_data = {
                "user_data": convert_date_to_string(user_data.model_dump()),
                "account_data": convert_date_to_string(account_data.model_dump()),
                "otp": otp
            }
            redis_client.set(redis_key, json.dumps(temp_data), ex=600)

            logging.info("OTP generated and stored in Redis for email: %s", account_data.email_address)

            return RegistrationResponse(
                message="User information received. OTP has been sent. Please verify to complete registration."
            )

        except Exception as e:
            logging.error(f"Unexpected error during registration: {e}\n{traceback.format_exc()}")
            return RegistrationResponse(message="An unexpected error occurred during registration.")


    async def verify_otp_and_register_user(self, otp_data):
        
        try:
            logger.info("Starting OTP verification and user registration.")

            email_address = otp_data.email_address.lower()
            redis_key = f"registration:{email_address}"

            logger.debug(f"Verifying OTP for email: {email_address}")
            otp_verification = await self.otp_service.verify_otp(redis_key, otp_data.otp)
            if otp_verification["status_code"] != 200:
                logger.warning(f"OTP verification failed for email: {email_address}. Reason: {otp_verification['message']}")
                raise OTPVerificationFailedError(otp_verification["message"])

            logger.debug("OTP verification successful. Proceeding with user registration.")
            user_data = otp_verification["user_data"]
            account_data = otp_verification["account_data"]

            logger.debug(f"Creating mailbox for email: {account_data['email_address']}")
            mailbox_response = await mailservice.create_mailbox(
                username=account_data["email_address"].split("@")[0],
                password=account_data["password"],
            )
            if mailbox_response["status"] == "error":
                logger.error(f"Failed to create mailbox for email: {account_data['email_address']}. Error: {mailbox_response['message']}")
                raise MailboxCreationFailedError(mailbox_response["message"])

            logger.debug("Creating user in the database.")
            user = await account_repository.create_user(self.db, UserCreate(**user_data))
            if not user:
                logger.error("Failed to create user during OTP verification.")
                raise UserCreationFailedError()

            # logger.debug("Setting default profile picture URL.")
            # account_data['image_url'] = self.default_profile_picture_url

            # logger.debug("Validating default profile picture URL.")

            # try:
            #     response = requests.get(self.default_profile_picture_url, timeout=5)
            #     if response.status_code != 200:
            #         logger.error(f"Default profile picture URL is inaccessible: {self.default_profile_picture_url}")
            #         raise ValueError(f"Default profile picture URL is inaccessible: {self.default_profile_picture_url}")
            #     logger.info("Default profile picture URL is valid and accessible.")
            # except requests.exceptions.RequestException as e:
            #     logger.error(f"Error while validating the profile picture URL: {e}")
            #     raise ValueError("Invalid default profile picture URL.") from e

            logger.debug("Creating account in the database.")
            account = await account_repository.create_account(self.db, AccountCreate(**account_data), user.user_id)
            if not account:
                logger.error(f"Failed to create account for user ID: {user.user_id}")
                raise AccountCreationFailedError()

            logger.debug("Creating SMTP credentials.")
            smtp_credentials = await smtp_repository.create_smtp_credentials(
                db=self.db, account_id=account.account_id, email_address=account_data["email_address"], smtp_password=account_data["password"]
            )
            if not smtp_credentials:
                logger.error(f"Failed to store SMTP credentials for account ID: {account.account_id}")
                raise SMTPCredentialCreationFailedError()

            logger.debug("Marking user as verified and committing changes.")
            user.is_verified = True
            await self.db.commit()

            logger.info(f"User registration and mailbox creation completed successfully for email: {email_address}")
            return RegistrationResponse(message="OTP verified successfully. Registration and mailbox creation complete.")

        except Exception as e:
            logger.error(f"Unexpected error during OTP verification: {e}", exc_info=True)
            raise OTPVerificationFailedError("An unexpected error occurred during OTP verification.")
            await self.db.rollback()

    async def resend_otp(self, otp_data: ResendOTPSchema):
        try:
            # Generate a new OTP
            otp = otp_service.generate_otp()

            # Use email address as Redis key, so that OTP is associated with the specific user
            redis_key = f"registration:{otp_data.email_address.lower()}"  

            existing_data = redis_client.get(redis_key)
            if existing_data:
                existing_data = json.loads(existing_data)
            else:
                # If no existing data, set up a new template, but no need for account data
                existing_data = {
                    "email_address": otp_data.email_address.lower(),
                }

            # Update only the OTP in Redis
            existing_data["otp"] = otp

            # Store the updated OTP data in Redis with an expiration time of 600 seconds (10 minutes)
            redis_client.set(redis_key, json.dumps(existing_data), ex=600)

            # Log the generated OTP for debugging
            logging.info(f"Generated OTP for email {otp_data.email_address}: {otp}") 

            # Return success response
            return {
                "status_code": 200,
                "message": "OTP has been generated and would typically be sent to the user.",
            }

        except Exception as e:
            logger.error(f"Unexpected error during OTP resend: {e}", exc_info=True)
            raise OTPResendFailedError("An unexpected error occurred during OTP resend.")



class AccountService:
    def __init__(self, db: AsyncSession = Depends(get_db)):  
        self.db = db

    async def get_status(self, user_id:int) -> str:
        account = await account_repository.get_account_by_user_id(self.db, user_id)
        if not account:
            raise HTTPException(
            status_code=404,
            detail="Account not found"
        )
        if not account.status:
            return ""
        logger.info("Account status:{account.status}")
        return account.status

