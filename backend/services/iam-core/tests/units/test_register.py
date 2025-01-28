import pytest
from iam.app.services.register_service import RegistrationService
from iam.app.domain.schemas.accounts_schema import UserCreate, AccountCreate
from unittest.mock import AsyncMock, patch
@pytest.mark.asyncio
async def test_register_user_success():
    # Mock data
    user_data = UserCreate(first_name="John", last_name="Doe", gender="male",birthday = "1990-11-15", phone_number="+1234567890")
    account_data = AccountCreate(email_address="john@buzzbox.com", password="StrongP@ssword123", status="", recovery_email= "")

    # Mock services
    mock_db = AsyncMock()
    mock_redis_client = AsyncMock()
    mock_otp_service = AsyncMock()
    mock_otp_service.generate_otp.return_value = "123456"

    registration_service = RegistrationService()

    with patch("MailService_Project.IAM_Service.app.infrastructure.repositories.account_repository.get_account_by_email", return_value=None):
        with patch("MailService_Project.IAM_Service.app.infrastructure.repositories.account_repository.get_user_by_phone", return_value=None):
            with patch("MailService_Project.IAM_Service.app.core.redis.redis_client", mock_redis_client):
                response = await registration_service.register_user(user_data, account_data, mock_db)

    assert response["status_code"] == 200
    assert response["message"] == "User information received. OTP has been sent. Please verify to complete registration."





@pytest.mark.asyncio
async def test_register_user_duplicate_email(caplog):
    user_data = UserCreate(
        first_name="qazal",
        last_name="naderi",
        gender="other",
        birthday="2012-04-05",
        phone_number="+19893845"
    )
    account_data = AccountCreate(
        email_address="qazalnad@buzzbox.com",
        password="@Qazal1234",
        status="",
        recovery_email=""
    )

    mock_db = AsyncMock()
    registration_service = RegistrationService()

    # Mock both email and phone number checks
    with patch(
            "MailService_Project.IAM_Service.app.infrastructure.repositories.account_repository.get_account_by_email",
            AsyncMock(return_value=AsyncMock())), \
            patch(
                "MailService_Project.IAM_Service.app.infrastructure.repositories.account_repository.get_user_by_phone",
                AsyncMock(return_value=None)):
        response = await registration_service.register_user(user_data, account_data, mock_db)



    # Assert the response
    assert response["status_code"] == 400
    assert "Email address already taken" in response["message"]

    # Check the captured logs
    captured = caplog.text
    assert "Unexpected error during registration" not in captured