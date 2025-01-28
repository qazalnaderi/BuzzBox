import pytest
from unittest.mock import AsyncMock
from ...app.services.login_service import LoginService
from ...app.domain.schemas.accounts_schema import AdminLogin, UserLogin, LoginResponse
from ...app.infrastructure.repositories import account_repository,admin_repository
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import  AsyncSession


@pytest.fixture
def mock_db():
    # Mock the database session for AsyncSession
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def login_service(mock_db):
    return LoginService(mock_db)


# Testing Admin Login
@pytest.mark.asyncio
async def test_admin_login_success(login_service, mock_db):
    # Prepare mock data
    admin_login = AdminLogin(email_address="admin@buzzbox.local", password="@Qazal1234")
    mock_admin = AsyncMock()
    mock_admin.admin_id = 2
    mock_admin.email_address = "admin@buzzbox.local"
    mock_db.return_value = mock_admin

    # Mock the repository call
    admin_repository.verify_admin_credentials = AsyncMock(return_value=mock_admin)

    response = await login_service.admin_login(admin_login)

    # Check the actual attributes of LoginResponse
    assert isinstance(response, LoginResponse)
    assert response.access_token is not None
    assert response.token_type == "bearer"


@pytest.mark.asyncio
async def test_admin_login_failure(login_service, mock_db):
    # Prepare mock data
    admin_login = AdminLogin(email_address="admin2@buzzbox.com", password="wrong_password")

    # Mock the repository call to return None (admin not found)
    admin_repository.verify_admin_credentials = AsyncMock(return_value=None)

    # Expecting an HTTPException on admin not found
    try:
        await login_service.admin_login(admin_login)
    except HTTPException as exc:
        assert exc.status_code == 400
        assert exc.detail == "Invalid username or password"



# Testing User Login
@pytest.mark.asyncio
async def test_user_login_success(login_service, mock_db):
    # Prepare mock data
    user_login = UserLogin(email_address="qazalnad@buzzbox.com", password="@Qazal1234")
    mock_user = AsyncMock()
    mock_user.user_id = 11
    mock_user.email_address = "qazalnad@buzzbox.com"
    mock_db.return_value = mock_user

    # Mock the repository call
    account_repository.verify_user_credentials = AsyncMock(return_value=mock_user)

    response = await login_service.user_login(user_login)

    # Check the actual attributes of LoginResponse
    assert isinstance(response, LoginResponse)
    assert response.access_token is not None
    assert response.token_type == "bearer"



@pytest.mark.asyncio
async def test_user_login_failure(login_service, mock_db):
    # Prepare mock data
    user_login = UserLogin(email_address="user@buzzbox.com", password="IAMservice1234#")

    # Mock the repository call to return None (user not found)
    account_repository.verify_user_credentials = AsyncMock(return_value=None)

    # Expecting an HTTPException on user not found
    try:
        await login_service.user_login(user_login)
    except HTTPException as exc:
        assert exc.status_code == 400
        assert exc.detail == "User not found"
