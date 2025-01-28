import pytest
from httpx import AsyncClient
from fastapi import status
from  app.main import app
from ...app.domain.schemas.media_schema import MediaSchema
# from motor.motor_asyncio import AsyncIOMotorGridOut
# Mock dependencies
@pytest.fixture
def mock_get_current_user():
    return lambda: {'email_address': 'user@example.com'}

@pytest.fixture
def mock_media_service():
    class MockMediaService:
        async def create_media(self, file, email_address):
            return MediaSchema(mongo_id="mock_id", filename=file.filename, content_type=file.content_type)

        async def get_media(self, media_id, email_address):
            if str(media_id) == "valid_id":
                return MediaSchema(mongo_id=media_id, filename="file.txt", content_type="text/plain"), lambda: b"File content"
            else:
                raise Exception("Media not found")

    return MockMediaService()

@pytest.fixture
def mock_account_service():
    class MockAccountService:
        async def get_account_profile(self, email_address):
            if email_address == "user@example.com":
                return type("MockUser", (), {"image_url": "valid_id"})
            return None

        async def update_profile_picture(self, email_address, media_url):
            pass

    return MockAccountService()

@pytest.fixture
def mock_communication_service():
    class MockCommunicationService:
        async def get_email_receiver(self, db, email_id):
            return type("MockReceiver", (), {"recipient_email": "recipient@example.com"})

        async def get_email_attachments(self, db, email_id):
            return ["valid_id"]

        async def upload_attachments(self, db, email_id, attachment_urls):
            pass

        async def get_email_by_id(self, db, email_id):
            return type("MockEmail", (), {"sender_id": 1})

    return MockCommunicationService()

@pytest.mark.asyncio
async def test_upload_profile_picture(mock_media_service, mock_get_current_user, mock_account_service):
    app.dependency_overrides[get_current_user] = mock_get_current_user
    app.dependency_overrides[MediaService] = lambda: mock_media_service
    app.dependency_overrides[AccountService] = lambda: mock_account_service

    file = ("test.jpg", b"filecontent", "image/jpeg")
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.put(
            "/profile/upload",
            files={"file": file}
        )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["filename"] == "test.jpg"

@pytest.mark.asyncio
async def test_get_user_profile(mock_media_service, mock_get_current_user, mock_account_service):
    app.dependency_overrides[get_current_user] = mock_get_current_user
    app.dependency_overrides[MediaService] = lambda: mock_media_service
    app.dependency_overrides[AccountService] = lambda: mock_account_service

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/get_user_profile/user@example.com")

    assert response.status_code == status.HTTP_200_OK
    assert "Content-Disposition" in response.headers

@pytest.mark.asyncio
async def test_upload_email_attachments(mock_media_service, mock_get_current_user, mock_communication_service):
    app.dependency_overrides[get_current_user] = mock_get_current_user
    app.dependency_overrides[MediaService] = lambda: mock_media_service
    app.dependency_overrides[CommunicationService] = lambda: mock_communication_service

    file = ("attachment.txt", b"attachment content", "text/plain")
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/email/attachments",
            files={"files": file},
            data={"email_id": 1}
        )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["filename"] == "attachment.txt"

@pytest.mark.asyncio
async def test_get_email_attachments(mock_media_service, mock_get_current_user, mock_communication_service):
    app.dependency_overrides[get_current_user] = mock_get_current_user
    app.dependency_overrides[MediaService] = lambda: mock_media_service
    app.dependency_overrides[CommunicationService] = lambda: mock_communication_service

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/email/attachments/1")

    assert response.status_code == status.HTTP_200_OK
    assert response.headers["Content-Type"] == "application/zip"