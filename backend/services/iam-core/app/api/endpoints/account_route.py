from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger
from app.services.account_service import RegistrationService, AccountService
from fastapi.responses import JSONResponse
from app.infrastructure.repositories.smtp_repository import create_smtp_credentials
from app.domain.schemas.accounts_schema import OTPCreate, UserSchema,AccountSchema
from app.services.auth_service.user_service import get_current_user
from app.domain.models.accounts import User, Account
import logging
from app.infrastructure.repositories import account_repository
from app.domain.schemas.accounts_schema import (
    UserCreate,
    AccountCreate,
    RegistrationResponse,
    ResendOTPSchema
)
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db.database import get_db
from app.helper import (
    OTPVerificationFailedError,
    MailboxCreationFailedError,
    UserCreationFailedError,
    AccountCreationFailedError,
    SMTPCredentialCreationFailedError,
    OTPResendFailedError    
)
from app.services.auth_service.otp_service import OTPService
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

user_router = APIRouter()

async def get_registration_service(db: AsyncSession = Depends(get_db)) -> RegistrationService:
    return RegistrationService(db)


@user_router.post(
    "/Register",
    status_code=status.HTTP_201_CREATED,
    response_model=RegistrationResponse
)
async def register_user(
    user: UserCreate,
    account: AccountCreate,
    account_service: Annotated[RegistrationService, Depends(get_registration_service)],
    db: AsyncSession = Depends(get_db),
) :
    result = await account_service.register_user(user, account)

    if "already registered" in result.message or "taken" in result.message:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result.message)
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": result.message},
    )


@user_router.post("/verify-otp")
async def verify_otp(
    otp_data: OTPCreate,
    account_service: Annotated[RegistrationService, Depends(get_registration_service)]):
    try:
        result = await account_service.verify_otp_and_register_user(otp_data)
        return JSONResponse(
            status_code=200, 
            content={"message": result.message} 
        )
    except OTPVerificationFailedError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except MailboxCreationFailedError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@user_router.post("/resend-otp")
async def resend_otp(
    otp_data: ResendOTPSchema,
    account_service: Annotated[RegistrationService, Depends(get_registration_service)]
):
    try:
        result = await account_service.resend_otp(otp_data)
        return JSONResponse(status_code=result["status_code"], content={"message": result["message"]})
    except OTPResendFailedError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

async def get_account_service(db: AsyncSession = Depends(get_db)) -> AccountService:
    return AccountService(db)


@user_router.get("/get-account-status")
async def get_account_status(user_id: int = Depends(get_current_user), account_service: AccountService = Depends(get_account_service)):
    try:
        status = await account_service.get_status(user_id)
        return {"status": status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    