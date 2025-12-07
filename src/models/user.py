from sqlalchemy import (
    Column, BigInteger, Integer, String, Numeric, SmallInteger,
    TIMESTAMP, ForeignKey
)
from sqlalchemy.orm import relationship

from core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_role_id = Column(BigInteger, nullable=False, default=3)

    name = Column(String(255), nullable=False)
    company_name = Column(String(255))
    original_language = Column(String(255))

    description_tr = Column(BigInteger, ForeignKey("mytrade.translations.id"))
    bin = Column(BigInteger)

    email = Column(String(255), nullable=False, unique=True)
    is_email_showed = Column(Integer, nullable=False, default=1)
    email_verified_at = Column(TIMESTAMP(timezone=True))

    password = Column(String(255), nullable=False)

    balance = Column(Numeric(10, 2), nullable=False, default=0.00)
    is_activated = Column(SmallInteger, nullable=False, default=0)
    moderation_status = Column(Integer, nullable=False, default=0)

    representative_phone = Column(String(255))
    entrepreneurial_activity_id = Column(BigInteger)

    remember_token = Column(String(100))

    story_image_slug = Column(String(255))
    story_video_slug = Column(String(255))

    meta_title_tr = Column(BigInteger, ForeignKey("mytrade.translations.id"))
    meta_description_tr = Column(BigInteger, ForeignKey("mytrade.translations.id"))
    meta_keywords_tr = Column(BigInteger, ForeignKey("mytrade.translations.id"))

    created_at = Column(TIMESTAMP(timezone=True))
    updated_at = Column(TIMESTAMP(timezone=True))

    about_tr = Column(BigInteger, ForeignKey("mytrade.translations.id"))

    rating = Column(Numeric(2, 1), nullable=False, default=0.0)
    reviews_count = Column(BigInteger, nullable=False, default=0)

    stripe_id = Column(String(255))
    pm_type = Column(String(255))
    pm_last_four = Column(String(4))

    trial_ends_at = Column(TIMESTAMP(timezone=True))
    page_description_tr = Column(BigInteger, ForeignKey("mytrade.translations.id"))

    is_logo_on_home = Column(Integer, nullable=False, default=0)
    logo_on_home_date = Column(TIMESTAMP(timezone=True))

    provider = Column(String(255))
    provider_id = Column(String(255))

    tname_tr = Column(BigInteger, ForeignKey("mytrade.translations.id"))
    tcompany_name_tr = Column(BigInteger, ForeignKey("mytrade.translations.id"))

    meta_status = Column(SmallInteger, nullable=False, default=0)

    sent_messages = relationship("Message", back_populates="sender")
    buyer_chats = relationship("Chat", foreign_keys="[Chat.buyer_id]", back_populates="buyer")
