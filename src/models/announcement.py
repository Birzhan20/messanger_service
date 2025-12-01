from sqlalchemy import (
    Column, BigInteger, Integer, String, TIMESTAMP, Time,
    ForeignKey
)
from sqlalchemy.orm import declarative_base, relationship

from core.database import Base


class Announcement(Base):
    __tablename__ = "announcements"

    id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True)

    user_id = Column(BigInteger)
    product_id = Column(BigInteger)
    deal_type_id = Column(BigInteger)

    email = Column(String(255))
    original_language = Column(String(255))

    count_view = Column(Integer, nullable=False, default=0)
    count_favorite = Column(Integer, nullable=False, default=0)
    count_phone = Column(Integer, nullable=False, default=0)
    count_email = Column(Integer, nullable=False, default=0)
    count_chat = Column(Integer, nullable=False, default=0)

    is_autorenewal = Column(Integer, nullable=False, default=0)

    engine_volume = Column(String(255))
    mileage = Column(String(255))
    mileage_status = Column(Integer, nullable=False, default=0)

    number_of_seats = Column(String(255))

    plot_area = Column(String(255))
    plot_area_status = Column(Integer, nullable=False, default=0)

    number_of_rooms = Column(String(255))
    total_area = Column(String(255))
    living_area = Column(String(255))
    kitchen_area = Column(String(255))

    plot_area_acres = Column(String(255))
    how_plot_fenced_general = Column(String(255))

    floor_of = Column(String(255))
    floor = Column(String(255))

    year_construction = Column(String(255))
    name_country_estate = Column(String(255))

    total_area_room = Column(String(255))
    total_area_room_status = Column(Integer, nullable=False, default=0)

    area_territory = Column(String(255))
    area_territory_status = Column(Integer, nullable=False, default=0)

    ceiling_height = Column(String(255))
    name_object = Column(String(255))
    dedicated_power = Column(String(255))
    year_foundation = Column(String(255))

    area_house = Column(String(255))
    production_area = Column(String(255))
    warehouse_area = Column(String(255))
    office_space = Column(String(255))
    roof_covering = Column(String(255))

    number_bathrooms = Column(String(255))
    area_object = Column(String(255))
    number_seats_for_car = Column(String(255))

    first_square = Column(String(255))
    second_square = Column(String(255))

    created_at = Column(TIMESTAMP(timezone=True))
    updated_at = Column(TIMESTAMP(timezone=True))

    is_vip = Column(Integer, nullable=False, default=0)
    vip_date = Column(TIMESTAMP(timezone=True))

    is_hot = Column(Integer, nullable=False, default=0)
    hot_date = Column(TIMESTAMP(timezone=True))

    published_time = Column(Time)
    unpublish_time = Column(Time)

    chats = relationship("Chat", back_populates="announcement")