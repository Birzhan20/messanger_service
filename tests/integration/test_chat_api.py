import pytest
from unittest.mock import patch
from models.user import User
from models.announcement import Announcement
from models.chat import Chat

@pytest.mark.asyncio
async def test_start_chat_api(client, db_session):
    # Setup
    seller = User(id=10, name="Seller", email="seller_api@example.com", password="pass")
    buyer = User(id=11, name="Buyer", email="buyer_api@example.com", password="pass")
    db_session.add_all([seller, buyer])
    await db_session.commit()
    
    ad = Announcement(id=10, user_id=seller.id)
    db_session.add(ad)
    await db_session.commit()
    
    # Call API
    response = await client.post(f"/chat/start/{ad.id}?user_id={buyer.id}")
    assert response.status_code == 200
    data = response.json()
    assert "chat_id" in data


@pytest.mark.asyncio
async def test_send_message_api(client, db_session):
    # Setup
    seller = User(id=12, name="Seller", email="seller_api2@example.com", password="pass")
    buyer = User(id=13, name="Buyer", email="buyer_api2@example.com", password="pass")
    db_session.add_all([seller, buyer])
    await db_session.commit()
    
    ad = Announcement(id=11, user_id=seller.id)
    db_session.add(ad)
    await db_session.commit()
    
    chat = Chat(id=10, announcement_id=ad.id, buyer_id=buyer.id)
    db_session.add(chat)
    await db_session.commit()
    
    # Call API
    response = await client.post(f"/chat/{chat.id}/send?user_id={buyer.id}&text=HelloAPI")
    assert response.status_code == 200
    data = response.json()
    assert data["message_text"] == "HelloAPI"


@pytest.mark.asyncio
async def test_my_chats_api(client, db_session):
    # Setup
    seller = User(id=14, name="Seller", email="seller_api3@example.com", password="pass")
    buyer = User(id=15, name="Buyer", email="buyer_api3@example.com", password="pass")
    db_session.add_all([seller, buyer])
    await db_session.commit()
    
    ad = Announcement(id=12, user_id=seller.id)
    db_session.add(ad)
    await db_session.commit()
    
    chat = Chat(id=11, announcement_id=ad.id, buyer_id=buyer.id, last_message_text="Test")
    db_session.add(chat)
    await db_session.commit()
    
    # Call API
    response = await client.get(f"/chat/my?user_id={buyer.id}&tab=buying")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["partner_name"] == "Seller"
