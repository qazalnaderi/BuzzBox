from sqlalchemy.ext.asyncio import AsyncSession
import logging
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from app.core.redis.redis_client import redis_client
from app.services.auth_service.user_service import get_current_user
from app.infrastructure.repositories.account_repository import get_user_by_id, get_account_by_user_id, get_account_by_email, verify_user_credentials
from app.services.profile_management_service import UpdateProfileService, ChangePasswordService, ResetPasswordService, DeleteAccountService
from app.core.db.database import get_db
from app.domain.schemas.profile_management_schema import (UpdateProfile, UpdatedProfileResponse,
                                                         ChangePasswordRequest, ChangePasswordResponse,
                                                         PasswordResetRequest, PasswordResetResponse, DeleteAccountRequest)
from app.services.auth_service.otp_service import OTPService
import json
profile_router = APIRouter()

@profile_router.put("/update-profile", response_model=UpdatedProfileResponse)
async def update_profile(
    profile_data: UpdateProfile,
    user_id: int = Depends(get_current_user),  
    db: AsyncSession = Depends(get_db)
):
    user = await get_user_by_id(db, user_id) 
    logging.info(f"User fetched: {user}")
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    update_service = UpdateProfileService(db)
    updated_profile = await update_service.update_profile(user.user_id, profile_data.dict())

    return updated_profile


@profile_router.put("/change-password", response_model=ChangePasswordResponse)
async def change_password(
        password_data: ChangePasswordRequest,
        user_id: int = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    user = await get_user_by_id(db, user_id)  
    logging.info(f"User fetched: {user}")
    logging.info(f"making sure router gets user_id correctly: {user.user_id}")

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    change_password_service = ChangePasswordService(db)
    try:
        updated_user = await change_password_service.change_password(user.user_id, password_data.dict())
        return updated_user

    except HTTPException as e:
        logging.error(f"Error changing password: {str(e.detail)}")
        raise e
    except Exception as e:
        logging.error(f"Unexpected error changing password: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


otp_service = OTPService()


@profile_router.post("/request-password-reset")
async def request_password_reset(email_address: str, db: AsyncSession = Depends(get_db)):
    account = await get_account_by_email(db, email_address)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found with the provided email address")

    otp = otp_service.generate_otp()
    redis_key = f"password_reset:{otp}"  

    temp_data = {
        "email_address": email_address.lower(),
        "otp": otp,
        "user_data": {"email_address": email_address.lower()},
        "account_data": {"email_address": email_address.lower()} 
    }

    redis_client.set(redis_key, json.dumps(temp_data), ex=600)  
    logging.info(f"Generated OTP for email {email_address}: {otp}") 

    return {
        "status_code": 200,
        "message": "OTP has been generated and would typically be sent to the user.",
    }


@profile_router.post("/verify-otp-and-reset-password",
                     response_model=PasswordResetResponse,
                     status_code=200,
                     responses={400: {"model": PasswordResetResponse}, 500: {"model": PasswordResetResponse}})
async def verify_otp_and_reset_password(
    password_reset_request: PasswordResetRequest,
    db: AsyncSession = Depends(get_db)
):
    reset_password_service = ResetPasswordService(db)
    try:
        otp = password_reset_request.otp
        redis_key = f"password_reset:{otp}"
        otp_verification = await otp_service.verify_otp(redis_key, otp)

        if otp_verification["status_code"] != 200:
            raise HTTPException(status_code=otp_verification["status_code"], detail=otp_verification["message"])
        email_address = otp_verification["user_data"]["email_address"]
        updated_account = await reset_password_service.reset_password(
            email_address=email_address,
            new_password=password_reset_request.new_password,
            confirm_password=password_reset_request.confirm_password,
        )
        await otp_service.delete_otp(redis_key)
        return PasswordResetResponse(
            status_code=200, message="Password reset successfully"
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        logging.error(f"Unexpected error resetting password: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@profile_router.delete("/delete-account", status_code=200)

async def delete_account(
    delete_request: DeleteAccountRequest,
    user_id: int = Depends(get_current_user),  
    db: AsyncSession = Depends(get_db)
):

    logging.info(f"Starting account deletion process for user_id: {user_id}")
    try:
        if delete_request.password != delete_request.confirm_password:
            logging.warning("Password and confirmation password do not match")
            raise HTTPException(status_code=400, detail="Passwords do not match")

        logging.info("Verifying user password")
        account = await get_account_by_user_id(db, user_id)
        if not account:
            logging.error(f"No account found for user_id: {user_id}")
            raise HTTPException(status_code=404, detail="Account not found")

        is_password_valid = await verify_user_credentials(db, account.email_address, delete_request.password)
        if not is_password_valid:
            logging.warning(f"Invalid password for user_id: {user_id}")
            raise HTTPException(status_code=403, detail="Invalid password")
            
        delete_account_service = DeleteAccountService(db)

        logging.info(f"Deleting account for account_id: {account.account_id}")
        success = await delete_account_service.delete_account(account.account_id)

        if not success:
            logging.error(f"Account deletion failed for account_id: {account.account_id}")
            raise HTTPException(status_code=404, detail="Account not found")

        logging.info(f"Account deletion successful for user_id: {user_id}")
        return {"message": "Account deleted successfully"}
    except HTTPException as e:
        logging.error(f"HTTPException during account deletion: {e.detail}")
        raise e
    except Exception as e:
        logging.exception(f"Unexpected error during account deletion for user_id: {user_id}")
        raise HTTPException(status_code=500, detail="Internal server error")