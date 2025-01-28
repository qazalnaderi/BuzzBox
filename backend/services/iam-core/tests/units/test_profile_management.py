import pytest
from unittest.mock import AsyncMock
from app.services.profile_management_service import UpdateProfileService, ChangePasswordService, ResetPasswordService
from app.domain.schemas.profile_management_schema import (
    UpdateProfile, UpdatedProfileResponse,
    ChangePasswordRequest, ChangePasswordResponse,
    PasswordResetRequest, PasswordResetResponse
)
from app.infrastructure.repositories import account_repository
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.redis.redis_client import redis_client

from unittest.mock import MagicMock

@pytest.fixture
def mock_db():
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def update_profile_service(mock_db):
    return UpdateProfileService(mock_db)


@pytest.fixture
def change_password_service(mock_db):
    return ChangePasswordService(mock_db)


@pytest.fixture
def reset_password_service(mock_db):
    return ResetPasswordService(mock_db)


import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException

@pytest.mark.asyncio
async def test_update_profile_success(update_profile_service, mock_db):
    # Prepare mock data
    profile_data = UpdateProfile(
        previous_email_address= "ilianaderi@buzzbox.com",
        new_email_address= "",
        first_name= "ilia",
        last_name= "nad",
        gender= "",
        birthday= "2003-12-01",
        phone_number= ""
    )
    
   # Create mock user and account objects
    mock_user = MagicMock()
    mock_user.user_id = 3
    mock_user.first_name = 'John'
    mock_user.last_name = 'Doe'
    mock_user.email_address = 'john.doe@oldemail.com'
    mock_user.phone_number = '1234567890'

    mock_account = MagicMock()
    mock_account.email_address = 'john.doe@oldemail.com'
    mock_account.password = 'hashed_password'

    # Mocking the repository methods
    account_repository.get_user_by_id = AsyncMock(return_value=mock_user)
    account_repository.get_account_by_email = AsyncMock(return_value=mock_account)
    account_repository.update_user_and_account = AsyncMock(return_value=(mock_user, mock_account))

    # Mock the validation services
    mock_email_validation_service = MagicMock()
    mock_email_validation_service.validate_email = AsyncMock(return_value=None)
    mock_phone_validation_service = MagicMock()
    mock_phone_validation_service.validate_phone_number = AsyncMock(return_value=None)

    # Inject mocked services into the update_profile_service
    update_profile_service.email_validation_service = mock_email_validation_service
    update_profile_service.phone_validation_service = mock_phone_validation_service

    # Perform the update profile operation
    response = await update_profile_service.update_profile(3, profile_data)

    # Validate the response
    assert response.message == "Profile updated successfully"
    assert response.email_address == 'john.doe@oldemail.com'

@pytest.mark.asyncio
async def test_update_profile_user_not_found(update_profile_service, mock_db):
    # Prepare mock data
    profile_data = UpdateProfile(
        previous_email_address="ilia123naderi@buzzbox.com",
        new_email_address="",
        first_name="ilia",
        last_name="nad",
        gender="",
        birthday="2003-12-01",
        phone_number=""
    )

    # Use AsyncMock with None return values
    update_profile_service.account_repository.get_user_by_id = AsyncMock(return_value=None)
    update_profile_service.account_repository.get_account_by_email = AsyncMock(return_value=None)

    with pytest.raises(HTTPException) as exc_info:
        await update_profile_service.update_profile(3, profile_data.model_dump())
    assert exc_info.value.status_code == 404

@pytest.mark.asyncio
async def test_change_password_success(change_password_service, mock_db):
    # Prepare mock data
    password_data = ChangePasswordRequest(
        current_password="@Ilia1234",
        new_password="@Qazal1234",
        confirm_new_password="@Qazal1234"
    )

    # Create proper mock objects
    mock_user = MagicMock()
    mock_user.user_id = 3
    mock_user.email_address = "ilianaderi@example.com"

    mock_account = MagicMock()
    mock_account.password = "hashed_password"
    mock_account.email_address = "ilianaderi@example.com"

    # Use AsyncMock for repository methods
    account_repository.get_user_by_id = AsyncMock(return_value=mock_user)
    account_repository.get_account_by_user_id = AsyncMock(return_value=mock_account)
    account_repository.update_account_password = AsyncMock(return_value=mock_account)

    # Create and inject mock hash service
    mock_hash_service = MagicMock()
    mock_hash_service.verify_password.return_value = True
    mock_hash_service.hash_password.return_value = "new_hashed_password"
    change_password_service.hash_service = mock_hash_service

    response = await change_password_service.change_password(3, password_data.model_dump())

    assert isinstance(response, ChangePasswordResponse)
    assert response.message == "Password updated successfully"



@pytest.mark.asyncio
async def test_change_password_invalid_current_password(change_password_service, mock_db):
    # Prepare mock data
    password_data = ChangePasswordRequest(
        current_password="@Qazal1234",
        new_password="@Qazal1234",
        confirm_new_password="newpass123"  # Match the field name in implementation
    )
    mock_user = AsyncMock()
    mock_user.user_id = 3

    # Mock the repository calls
    account_repository.get_user_by_id = AsyncMock(return_value=mock_user)
    account_repository.verify_current_password = AsyncMock(return_value=False)

    with pytest.raises(HTTPException) as exc_info:
        await change_password_service.change_password(1, password_data.dict())
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "New passwords do not match"
