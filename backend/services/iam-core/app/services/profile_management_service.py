from sqlalchemy.ext.asyncio import AsyncSession
from ..helper import validate_email, validate_phone_number, check_password_strength
import logging
from .auth_service.hash_service import HashService
from fastapi.responses import JSONResponse
from ..domain.schemas.profile_management_schema import UpdatedProfileResponse, ChangePasswordResponse
from fastapi import  HTTPException
from ..helper import suggest_email
from ..infrastructure.repositories.account_repository import(get_account_by_email, get_user_by_id,
get_account_by_user_id,get_all_account_belongsto_user_id, delete_account, get_account_by_id,
delete_emails_by_account,delete_reports_by_account, delete_user)
from ..infrastructure.repositories.profile_management_repository import update_user_and_account, update_account_password

hash_service = HashService()

class UpdateProfileService:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def update_profile(self, user_id: int, profile_data: dict):
        try:
            # Extract email and phone number from profile_data
            new_email = profile_data.get("new_email_address")
            prev_email = profile_data.get("previous_email_address")
            phone_number = profile_data.get("phone_number")

            account = await get_account_by_email(self.db, prev_email)
            if not account:
                raise HTTPException(status_code=404, detail="Account not found")

            # Validate email if provided
            if  new_email:
                logging.info(f"Validating  new_email: {new_email}")
                email_validation_error = await validate_email(new_email)
                if email_validation_error:
                    raise HTTPException(status_code=400, detail=email_validation_error)

                # Check if email already exists
                existing_email = await get_account_by_email(self.db, new_email)
                if existing_email:
                    suggested_email = await suggest_email(profile_data.get("first_name"), profile_data.get("last_name"))
                    raise HTTPException(status_code=400, detail=f"Email address already taken. Suggested: {suggested_email}")

            # Validate phone number if provided
            if phone_number:
                logging.info(f"Validating phone number: {phone_number}")
                phone_number_error = await validate_phone_number(phone_number)
                if phone_number_error:
                    raise HTTPException(status_code=400, detail=phone_number_error)

            # Fetch the user and their associated account
            user = await get_user_by_id(self.db, user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")


            # Update the user and account
            updated_user, updated_account = await update_user_and_account(
                self.db, user, account, profile_data
            )

            # Prepare the response
            response = UpdatedProfileResponse(
                email_address=updated_account.email_address,
                message="Profile updated successfully",
            )
            return response

        except HTTPException as e:
            logging.error(f"Validation error: {e.detail}")
            raise e
        except Exception as e:
            logging.error(f"Error updating profile: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")


class ChangePasswordService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def change_password(self, user_id: int, password_data: dict):
        try:
            # Extract the current and new passwords
            current_password = password_data.get("current_password")
            new_password = password_data.get("new_password")
            confirm_new_password = password_data.get("confirm_new_password")

            # Validate that the new password and confirmation match
            if new_password != confirm_new_password:
                raise HTTPException(status_code=400, detail="New passwords do not match")

            # Validate new password strength (e.g., length, complexity)
            password_validation_error = await check_password_strength(new_password)
            if password_validation_error:
                raise HTTPException(status_code=400, detail=password_validation_error)

            # Fetch the user from the database
            user = await get_user_by_id(self.db, user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            # Fetch the user's account and verify the current password
            account = await get_account_by_user_id(self.db, user_id)
            if not account:
                raise HTTPException(status_code=404, detail="Account not found")

            # Verify the current password using hashed password comparison
            if not hash_service.verify_password(current_password, account.password):
                raise HTTPException(status_code=400, detail="Current password is incorrect")

            # Hash the new password before storing it
            hashed_new_password = hash_service.hash_password(new_password)

            # Update the password in the database (assuming `update_account_password` updates the user's account)
            updated_account = await update_account_password(self.db, account, hashed_new_password)

            # Return a response message
            response = ChangePasswordResponse(
                message="Password updated successfully"
            )
            return response

        except HTTPException as e:
            logging.error(f"Validation error: {e.detail}")
            raise e
        except Exception as e:
            logging.error(f"Error changing password: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")


class ResetPasswordService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def reset_password(self, email_address: str, new_password: str, confirm_password: str):
        try:
            # Validate that passwords match
            if new_password != confirm_password:
                raise HTTPException(status_code=400, detail="Passwords do not match")

            # Validate password strength
            password_validation_error = await check_password_strength(new_password)
            if password_validation_error:
                raise HTTPException(status_code=400, detail=password_validation_error)

            # Fetch the account from the repository
            account = await get_account_by_email(self.db, email_address)
            if not account:
                raise HTTPException(status_code=404, detail="Account not found with the provided email address")

            # Hash the new password
            hashed_password = hash_service.hash_password(new_password)

            # Update the password using the repository
            updated_account = await update_account_password(self.db, account, hashed_password)

            return updated_account

        except HTTPException as e:
            logging.error(f"Validation error: {e.detail}")
            raise e
        except Exception as e:
            logging.error(f"Error resetting password: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")



class DeleteAccountService:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def delete_account(self, account_id: int) -> bool:
        try:
            logging.info(f"Fetching account with account_id: {account_id}")
            account = await get_account_by_id(self.db, account_id)
            if not account:
                logging.warning(f"Account not found for account_id: {account_id}")
                return False

            logging.info(f"Deleting reports for account_id: {account_id}")
            await delete_reports_by_account(self.db, account_id)

            logging.info(f"Deleting emails for account_id: {account_id}")
            await delete_emails_by_account(self.db, account_id)

            user_id = account.user_id
            logging.info(f"Checking other accounts for user_id: {user_id}")
            other_accounts = await get_all_account_belongsto_user_id(self.db, user_id)

            logging.info(f"Deleting account with account_id: {account_id}")
            await delete_account(self.db, account)

            if len(other_accounts) == 1:
                logging.info(f"No other accounts exist for user_id: {user_id}. Deleting user.")
                user = await get_user_by_id(self.db, user_id)
                if user:
                    await delete_user(self.db, user)

            logging.info(f"Committing database changes for account_id: {account_id}")
            await self.db.commit()
            return True
        except Exception as e:
            logging.exception(f"Error occurred during account deletion for account_id: {account_id}")
            raise