import pytest
from datetime import datetime
from models.user import User
from models.announcement import Announcement
from models.chat import Chat
from crud.chat_service import get_or_create_chat, send_message, get_user_chats, get_chat_with_messages
from fastapi import HTTPException

@pytest.mark.asyncio
async def test_get_or_create_chat(db_session):
    # Setup
    seller = User(id=1, name="Seller", email="seller@example.com", password="pass", user_role_id=2)
    buyer = User(id=2, name="Buyer", email="buyer@example.com", password="pass", user_role_id=3)
    db_session.add_all([seller, buyer])
    await db_session.commit()
    
    ad = Announcement(id=1, user_id=seller.id, original_language="ru")
    db_session.add(ad)
    await db_session.commit()
    
    # Test Create
    chat = await get_or_create_chat(ad.id, buyer.id, db_session)
    assert chat.id is not None
    assert chat.announcement_id == ad.id
    assert chat.buyer_id == buyer.id
    
    # Test Get Existing
    chat2 = await get_or_create_chat(ad.id, buyer.id, db_session)
    assert chat2.id == chat.id


@pytest.mark.asyncio
async def test_send_message(db_session):
    # Setup
    seller = User(id=3, name="Seller", email="seller2@example.com", password="pass")
    buyer = User(id=4, name="Buyer", email="buyer2@example.com", password="pass")
    db_session.add_all([seller, buyer])
    await db_session.commit()
    
    ad = Announcement(id=2, user_id=seller.id)
    db_session.add(ad)
    await db_session.commit()
    
    chat = Chat(id=1, announcement_id=ad.id, buyer_id=buyer.id)
    db_session.add(chat)
    await db_session.commit()
    
    # Test Send
    msg = await send_message(chat.id, buyer.id, db_session, text="Hello")
    assert msg.message_text == "Hello"
    assert msg.sender_id == buyer.id
    
    # Verify Chat Update
    await db_session.refresh(chat)
    assert chat.last_message_text == "Hello"
    assert chat.last_message_type == "text"


@pytest.mark.asyncio
async def test_get_user_chats(db_session):
    # Setup
    seller = User(id=5, name="Seller", email="seller3@example.com", password="pass")
    buyer = User(id=6, name="Buyer", email="buyer3@example.com", password="pass")
    db_session.add_all([seller, buyer])
    await db_session.commit()
    
    ad = Announcement(id=3, user_id=seller.id)
    db_session.add(ad)
    await db_session.commit()
    
    chat = Chat(id=2, announcement_id=ad.id, buyer_id=buyer.id, last_message_text="Hi", last_message_at=datetime.now())
    db_session.add(chat)
    await db_session.commit()
    
    # Test Buyer View
    chats = await get_user_chats(db_session, buyer.id, tab="buying")
    assert len(chats) == 1
    assert chats[0]['partner_name'] == "Seller"
    
    # Test Seller View
    chats = await get_user_chats(db_session, seller.id, tab="selling")
    assert len(chats) == 1
    assert chats[0]['partner_name'] == "Buyer"
    
    # Test Search
    chats = await get_user_chats(db_session, buyer.id, search_query="Sell")
    assert len(chats) == 1
    
    chats = await get_user_chats(db_session, buyer.id, search_query="Nobody")
    assert len(chats) == 0
