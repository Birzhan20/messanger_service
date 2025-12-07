import sys
import os

# Add src to path
sys.path.append(os.path.join(os.getcwd(), "src"))

try:
    from models.chat import Chat
    from models.messages import Message
    from models.announcement import Announcement
    from models.user import User
    from schemas.chat import ChatListResponse, ChatDetailResponse
    from crud.chat_service import get_user_chats
    from api.v1.chat import router
    print("Imports successful!")
except ImportError as e:
    print(f"Import failed: {e}")
    sys.exit(1)
except Exception as e:
    print(f"An error occurred: {e}")
    sys.exit(1)
