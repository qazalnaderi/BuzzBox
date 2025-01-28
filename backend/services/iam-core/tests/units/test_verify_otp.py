import pytest
from unittest.mock import patch
from iam.app.services.auth_service.otp_service import OTPService
from iam.app.domain.schemas.accounts_schema import OTPCreate
@pytest.mark.asyncio
async def test_verify_otp_success():
    otp_data = OTPCreate(email_address="john@buzzbox.com", otp="123456")
    otp_service = OTPService()

    # Mock Redis get method with a valid JSON response
    mock_response = b'{"otp": "123456", "user_data": {"first_name": "John", "last_name": "Doe"}, "account_data": {"email_address": "john@buzzbox.com"}}'
    with patch("MailService_Project.IAM_Service.app.core.redis.redis_client.redis_client.get", return_value=mock_response):
        result = await otp_service.verify_otp(redis_key=f"registration:{otp_data.email_address.lower()}", otp=otp_data.otp)

        assert result["status_code"] == 200
        assert result["message"] == "OTP verified successfully"


@pytest.mark.asyncio
async def test_verify_otp_invalid_code():
    otp_data = OTPCreate(email_address="john@buzzbox.com", otp="000000")
    otp_service = OTPService()

    # Correctly mock the Redis client method by patching the correct path
    with patch("MailService_Project.IAM_Service.app.core.redis.redis_client.redis_client.get", return_value=b'{"otp": "123456", "user_data": {}, "account_data": {}}'):
        # Pass the correct arguments to verify_otp method
        result = await otp_service.verify_otp(redis_key=f"registration:{otp_data.email_address.lower()}", otp=otp_data.otp)
        assert result["status_code"] == 400
        assert result["message"] == "Invalid OTP"

