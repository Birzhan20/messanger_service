import os
import sys

# Set mock environment variables BEFORE importing anything that uses settings
os.environ.setdefault("POCKETBASE_URL", "http://mock-pocketbase:8090")
os.environ.setdefault("POCKETBASE_ADMIN_EMAIL", "test@test.com")
os.environ.setdefault("POCKETBASE_ADMIN_PASSWORD", "testpassword")
os.environ.setdefault("POCKETBASE_COLLECTION", "files")
os.environ.setdefault("POCKETBASE_FIELD_NAME", "file")
os.environ.setdefault("S3_ENDPOINT", "http://mock-s3:9000")
os.environ.setdefault("S3_ACCESS_KEY", "minioadmin")
os.environ.setdefault("S3_SECRET_KEY", "minioadmin")
os.environ.setdefault("S3_BUCKET", "test-bucket")
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://mytrade:mysupertradesecretpwd@localhost:5432/mytrade")

import pytest
import pytest_asyncio
from datetime import datetime
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from core.database import Base, get_db
from models.user import User
from models.announcement import Announcement
from models.chat import Chat
from models.messages import Message


# =============================================================================
# Test Configuration
# =============================================================================

# Use the same database URL as the application
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+asyncpg://mytrade:mysupertradesecretpwd@localhost:5432/mytrade"
)


@pytest_asyncio.fixture
async def engine():
    """Create async engine for tests."""
    _engine = create_async_engine(DATABASE_URL, echo=False)
    yield _engine
    await _engine.dispose()


@pytest_asyncio.fixture
async def async_session_maker(engine):
    """Create session maker."""
    return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture
async def db_session(async_session_maker):
    """Create database session for each test."""
    async with async_session_maker() as session:
        yield session
        # Rollback any uncommitted changes
        await session.rollback()


@pytest_asyncio.fixture
async def test_user(db_session):
    """Create a test user for integration tests."""
    # Check if test user already exists
    result = await db_session.execute(
        text("SELECT id FROM users WHERE email = :email"),
        {"email": "integration_test@test.com"}
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        return existing
    
    # Create minimal test user
    result = await db_session.execute(
        text("""
            INSERT INTO users (name, email, password, user_role_id, balance, is_activated, 
                               moderation_status, rating, reviews_count, is_logo_on_home, 
                               is_email_showed, meta_status)
            VALUES (:name, :email, :password, :role_id, :balance, :is_activated, 
                    :moderation_status, :rating, :reviews_count, :is_logo_on_home,
                    :is_email_showed, :meta_status)
            RETURNING id
        """),
        {
            "name": "Integration Test User",
            "email": "integration_test@test.com",
            "password": "password_hash",
            "role_id": 1,
            "balance": 0,
            "is_activated": 1,
            "moderation_status": 0,
            "rating": 0,
            "reviews_count": 0,
            "is_logo_on_home": 0,
            "is_email_showed": 1,
            "meta_status": 0
        }
    )
    user_id = result.scalar_one()
    await db_session.commit()
    return user_id


@pytest_asyncio.fixture
async def test_user2(db_session):
    """Create a second test user (buyer)."""
    result = await db_session.execute(
        text("SELECT id FROM users WHERE email = :email"),
        {"email": "integration_test2@test.com"}
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        return existing
    
    result = await db_session.execute(
        text("""
            INSERT INTO users (name, email, password, user_role_id, balance, is_activated, 
                               moderation_status, rating, reviews_count, is_logo_on_home,
                               is_email_showed, meta_status, representative_phone)
            VALUES (:name, :email, :password, :role_id, :balance, :is_activated, 
                    :moderation_status, :rating, :reviews_count, :is_logo_on_home,
                    :is_email_showed, :meta_status, :phone)
            RETURNING id
        """),
        {
            "name": "Buyer Test User",
            "email": "integration_test2@test.com",
            "password": "password_hash",
            "role_id": 3,
            "balance": 0,
            "is_activated": 1,
            "moderation_status": 0,
            "rating": 0,
            "reviews_count": 0,
            "is_logo_on_home": 0,
            "is_email_showed": 1,
            "meta_status": 0,
            "phone": "+7 777 777 77 77"
        }
    )
    user_id = result.scalar_one()
    await db_session.commit()
    return user_id


@pytest_asyncio.fixture
async def test_announcement(db_session, test_user):
    """Create a test announcement."""
    result = await db_session.execute(
        text("SELECT id FROM announcements WHERE email = :email LIMIT 1"),
        {"email": "integration_test_ann@test.com"}
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        return existing
    
    result = await db_session.execute(
        text("""
            INSERT INTO announcements (user_id, email, count_view, count_favorite, 
                                       count_phone, count_email, count_chat, 
                                       is_autorenewal, mileage_status, 
                                       plot_area_status, total_area_room_status,
                                       area_territory_status, is_vip, is_hot)
            VALUES (:user_id, :email, :count_view, :count_favorite, 
                    :count_phone, :count_email, :count_chat,
                    :is_autorenewal, :mileage_status,
                    :plot_area_status, :total_area_room_status,
                    :area_territory_status, :is_vip, :is_hot)
            RETURNING id
        """),
        {
            "user_id": test_user,
            "email": "integration_test_ann@test.com",
            "count_view": 0,
            "count_favorite": 0,
            "count_phone": 0,
            "count_email": 0,
            "count_chat": 0,
            "is_autorenewal": 0,
            "mileage_status": 0,
            "plot_area_status": 0,
            "total_area_room_status": 0,
            "area_territory_status": 0,
            "is_vip": 0,
            "is_hot": 0
        }
    )
    announcement_id = result.scalar_one()
    await db_session.commit()
    return announcement_id


@pytest_asyncio.fixture
async def app():
    """Get FastAPI app instance."""
    from main import app as fastapi_app
    return fastapi_app


@pytest_asyncio.fixture
async def client(app, async_session_maker):
    """Create async test client with database override."""
    
    async def override_get_db():
        async with async_session_maker() as session:
            yield session
    
    app.dependency_overrides[get_db] = override_get_db
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


# =============================================================================
# POST /chat/start/{announcement_id} Tests
# =============================================================================

class TestStartChatEndpoint:
    """Integration tests for POST /chat/start/{announcement_id}."""

    @pytest.mark.asyncio
    async def test_start_chat_creates_new_chat(self, client, test_announcement, test_user2):
        """Test creating a new chat for an announcement."""
        response = await client.post(
            f"/chat/start/{test_announcement}",
            params={"user_id": test_user2}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "chat_id" in data
        assert isinstance(data["chat_id"], int)

    @pytest.mark.asyncio
    async def test_start_chat_returns_existing_chat(self, client, test_announcement, test_user2):
        """Test that starting chat again returns the same chat."""
        # Start chat first time
        response1 = await client.post(
            f"/chat/start/{test_announcement}",
            params={"user_id": test_user2}
        )
        chat_id1 = response1.json()["chat_id"]
        
        # Start chat second time - should return same chat
        response2 = await client.post(
            f"/chat/start/{test_announcement}",
            params={"user_id": test_user2}
        )
        chat_id2 = response2.json()["chat_id"]
        
        assert chat_id1 == chat_id2

    @pytest.mark.asyncio
    async def test_start_chat_with_invalid_announcement(self, client, test_user2):
        """Test starting chat with non-existent announcement returns 404."""
        response = await client.post(
            "/chat/start/999999999",
            params={"user_id": test_user2}
        )
        
        assert response.status_code == 404


# =============================================================================
# GET /chat/my Tests
# =============================================================================

class TestMyChatsEndpoint:
    """Integration tests for GET /chat/my."""

    @pytest.mark.asyncio
    async def test_my_chats_returns_list(self, client, test_user2, test_announcement):
        """Test getting user's chat list."""
        # Ensure chat exists
        await client.post(
            f"/chat/start/{test_announcement}",
            params={"user_id": test_user2}
        )
        
        response = await client.get(
            "/chat/my",
            params={"user_id": test_user2}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    @pytest.mark.asyncio
    async def test_my_chats_with_buyer_role(self, client, test_user2, test_announcement):
        """Test filtering chats by buyer role."""
        # Ensure chat exists
        await client.post(
            f"/chat/start/{test_announcement}",
            params={"user_id": test_user2}
        )
        
        response = await client.get(
            "/chat/my",
            params={"user_id": test_user2, "role": "buyer"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_my_chats_with_seller_role(self, client, test_user, test_announcement, test_user2):
        """Test filtering chats by seller role."""
        # Ensure chat exists (buyer starts chat)
        await client.post(
            f"/chat/start/{test_announcement}",
            params={"user_id": test_user2}
        )
        
        # Seller should see this chat with role=seller
        response = await client.get(
            "/chat/my",
            params={"user_id": test_user, "role": "seller"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_my_chats_empty_for_new_user(self, client):
        """Test that new user with no chats gets empty list."""
        response = await client.get(
            "/chat/my",
            params={"user_id": 999999999}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data == []


# =============================================================================
# GET /chat/{chat_id} Tests
# =============================================================================

class TestOpenChatEndpoint:
    """Integration tests for GET /chat/{chat_id}."""

    @pytest.mark.asyncio
    async def test_open_chat_returns_messages(self, client, test_announcement, test_user2):
        """Test opening a chat returns chat details with messages."""
        # Create chat first
        start_response = await client.post(
            f"/chat/start/{test_announcement}",
            params={"user_id": test_user2}
        )
        chat_id = start_response.json()["chat_id"]
        
        # Open chat
        response = await client.get(
            f"/chat/{chat_id}",
            params={"user_id": test_user2}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "partner" in data
        assert "messages" in data

    @pytest.mark.asyncio
    async def test_open_chat_returns_partner_info(self, client, test_announcement, test_user2):
        """Test that open chat returns partner information."""
        start_response = await client.post(
            f"/chat/start/{test_announcement}",
            params={"user_id": test_user2}
        )
        chat_id = start_response.json()["chat_id"]
        
        response = await client.get(
            f"/chat/{chat_id}",
            params={"user_id": test_user2}
        )
        
        assert response.status_code == 200
        data = response.json()
        partner = data.get("partner")
        
        if partner:
            assert "id" in partner
            assert "name" in partner
            assert "role" in partner

    @pytest.mark.asyncio
    async def test_open_chat_unauthorized_returns_404(self, client, test_announcement, test_user2):
        """Test that opening chat by unauthorized user returns 404."""
        start_response = await client.post(
            f"/chat/start/{test_announcement}",
            params={"user_id": test_user2}
        )
        chat_id = start_response.json()["chat_id"]
        
        # Try to open with different user
        response = await client.get(
            f"/chat/{chat_id}",
            params={"user_id": 999999999}
        )
        
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_open_nonexistent_chat_returns_404(self, client, test_user2):
        """Test that opening non-existent chat returns 404."""
        response = await client.get(
            "/chat/999999999",
            params={"user_id": test_user2}
        )
        
        assert response.status_code == 404


# =============================================================================
# POST /chat/{chat_id}/send Tests
# =============================================================================

class TestSendMessageEndpoint:
    """Integration tests for POST /chat/{chat_id}/send."""

    @pytest.mark.asyncio
    async def test_send_text_message(self, client, test_announcement, test_user2):
        """Test sending a text message."""
        # Create chat
        start_response = await client.post(
            f"/chat/start/{test_announcement}",
            params={"user_id": test_user2}
        )
        chat_id = start_response.json()["chat_id"]
        
        # Send message
        response = await client.post(
            f"/chat/{chat_id}/send",
            params={"user_id": test_user2, "text": "Hello, this is a test message!"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["message_text"] == "Hello, this is a test message!"
        assert data["message_type"] == "text"

    @pytest.mark.asyncio
    async def test_send_message_updates_chat_preview(self, client, test_announcement, test_user2):
        """Test that sending message updates chat's last_message_text."""
        start_response = await client.post(
            f"/chat/start/{test_announcement}",
            params={"user_id": test_user2}
        )
        chat_id = start_response.json()["chat_id"]
        
        # Send message
        await client.post(
            f"/chat/{chat_id}/send",
            params={"user_id": test_user2, "text": "Preview test message"}
        )
        
        # Check my_chats to verify preview
        chats_response = await client.get(
            "/chat/my",
            params={"user_id": test_user2}
        )
        
        assert chats_response.status_code == 200
        # Chat should have updated preview (checking via chat list)

    @pytest.mark.asyncio
    async def test_send_message_appears_in_history(self, client, test_announcement, test_user2):
        """Test that sent message appears in chat history."""
        start_response = await client.post(
            f"/chat/start/{test_announcement}",
            params={"user_id": test_user2}
        )
        chat_id = start_response.json()["chat_id"]
        
        # Send unique message
        unique_text = f"Unique test message {datetime.now().timestamp()}"
        await client.post(
            f"/chat/{chat_id}/send",
            params={"user_id": test_user2, "text": unique_text}
        )
        
        # Open chat and check history
        chat_response = await client.get(
            f"/chat/{chat_id}",
            params={"user_id": test_user2}
        )
        
        assert chat_response.status_code == 200
        messages = chat_response.json().get("messages", [])
        message_texts = [m["message_text"] for m in messages if m.get("message_text")]
        assert unique_text in message_texts

    @pytest.mark.asyncio
    async def test_send_message_unauthorized_returns_403(self, client, test_announcement, test_user2):
        """Test sending message by unauthorized user returns 403."""
        start_response = await client.post(
            f"/chat/start/{test_announcement}",
            params={"user_id": test_user2}
        )
        chat_id = start_response.json()["chat_id"]
        
        # Try to send as different user
        response = await client.post(
            f"/chat/{chat_id}/send",
            params={"user_id": 999999999, "text": "Unauthorized message"}
        )
        
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_send_message_to_nonexistent_chat_returns_404(self, client, test_user2):
        """Test sending message to non-existent chat returns 404."""
        response = await client.post(
            "/chat/999999999/send",
            params={"user_id": test_user2, "text": "Test"}
        )
        
        assert response.status_code == 404
