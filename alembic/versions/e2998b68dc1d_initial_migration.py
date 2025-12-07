"""Initial messenger_project schema

Revision ID: 2025_initial
Revises: 
Create Date: 2025-11-28 16:30:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = '2025_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.BigInteger(), primary_key=True),
        sa.Column('user_role_id', sa.BigInteger(), nullable=False, server_default='3'),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('company_name', sa.String(255)),
        sa.Column('original_language', sa.String(255)),
        sa.Column('description_tr', sa.BigInteger()),
        sa.Column('bin', sa.BigInteger()),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('is_email_showed', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('email_verified_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('password', sa.String(255), nullable=False),
        sa.Column('balance', sa.Numeric(10, 2), nullable=False, server_default='0.00'),
        sa.Column('is_activated', sa.SmallInteger(), nullable=False, server_default='0'),
        sa.Column('moderation_status', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('representative_phone', sa.String(255)),
        sa.Column('entrepreneurial_activity_id', sa.BigInteger()),
        sa.Column('remember_token', sa.String(100)),
        sa.Column('story_image_slug', sa.String(255)),
        sa.Column('story_video_slug', sa.String(255)),
        sa.Column('meta_title_tr', sa.BigInteger()),
        sa.Column('meta_description_tr', sa.BigInteger()),
        sa.Column('meta_keywords_tr', sa.BigInteger()),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('about_tr', sa.BigInteger()),
        sa.Column('rating', sa.Numeric(2, 1), nullable=False, server_default='0.0'),
        sa.Column('reviews_count', sa.BigInteger(), nullable=False, server_default='0'),
        sa.Column('stripe_id', sa.String(255)),
        sa.Column('pm_type', sa.String(255)),
        sa.Column('pm_last_four', sa.String(4)),
        sa.Column('trial_ends_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('page_description_tr', sa.BigInteger()),
        sa.Column('is_logo_on_home', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('logo_on_home_date', sa.TIMESTAMP(timezone=True)),
        sa.Column('provider', sa.String(255)),
        sa.Column('provider_id', sa.String(255)),
        sa.Column('tname_tr', sa.BigInteger()),
        sa.Column('tcompany_name_tr', sa.BigInteger()),
        sa.Column('meta_status', sa.SmallInteger(), nullable=False, server_default='0'),
    )

    op.create_table(
        'announcements',
        sa.Column('id', sa.BigInteger(), primary_key=True),
        sa.Column('user_id', sa.BigInteger()),
        sa.Column('product_id', sa.BigInteger()),
        sa.Column('deal_type_id', sa.BigInteger()),
        sa.Column('email', sa.String(255)),
        sa.Column('original_language', sa.String(255)),
        sa.Column('count_view', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('count_favorite', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('count_phone', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('count_email', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('count_chat', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_autorenewal', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('engine_volume', sa.String(255)),
        sa.Column('mileage', sa.String(255)),
        sa.Column('mileage_status', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('number_of_seats', sa.String(255)),
        sa.Column('plot_area', sa.String(255)),
        sa.Column('plot_area_status', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('number_of_rooms', sa.String(255)),
        sa.Column('total_area', sa.String(255)),
        sa.Column('living_area', sa.String(255)),
        sa.Column('kitchen_area', sa.String(255)),
        sa.Column('plot_area_acres', sa.String(255)),
        sa.Column('how_plot_fenced_general', sa.String(255)),
        sa.Column('floor_of', sa.String(255)),
        sa.Column('floor', sa.String(255)),
        sa.Column('year_construction', sa.String(255)),
        sa.Column('name_country_estate', sa.String(255)),
        sa.Column('total_area_room', sa.String(255)),
        sa.Column('total_area_room_status', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('area_territory', sa.String(255)),
        sa.Column('area_territory_status', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('ceiling_height', sa.String(255)),
        sa.Column('name_object', sa.String(255)),
        sa.Column('dedicated_power', sa.String(255)),
        sa.Column('year_foundation', sa.String(255)),
        sa.Column('area_house', sa.String(255)),
        sa.Column('production_area', sa.String(255)),
        sa.Column('warehouse_area', sa.String(255)),
        sa.Column('office_space', sa.String(255)),
        sa.Column('roof_covering', sa.String(255)),
        sa.Column('number_bathrooms', sa.String(255)),
        sa.Column('area_object', sa.String(255)),
        sa.Column('number_seats_for_car', sa.String(255)),
        sa.Column('first_square', sa.String(255)),
        sa.Column('second_square', sa.String(255)),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('is_vip', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('vip_date', sa.TIMESTAMP(timezone=True)),
        sa.Column('is_hot', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('hot_date', sa.TIMESTAMP(timezone=True)),
        sa.Column('published_time', sa.Time()),
        sa.Column('unpublish_time', sa.Time()),
    )

    op.create_table(
        'chats',
        sa.Column('id', sa.BigInteger(), primary_key=True),
        sa.Column('user1_id', sa.BigInteger()),
        sa.Column('user2_id', sa.BigInteger()),
        sa.ForeignKeyConstraint(['user1_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user2_id'], ['users.id'], ondelete='CASCADE'),
    )

    op.create_table(
        'messages',
        sa.Column('id', sa.BigInteger(), primary_key=True),
        sa.Column('sender_id', sa.BigInteger()),
        sa.Column('receiver_id', sa.BigInteger()),
        sa.Column('content', sa.Text()),
        sa.Column('timestamp', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('file_id', sa.BigInteger()),
        sa.Column('chat_id', sa.Integer()),
        sa.ForeignKeyConstraint(['sender_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['receiver_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['chat_id'], ['chats.id'], ondelete='CASCADE'),
    )


def downgrade():
    op.drop_table('messages')
    op.drop_table('chats')
    op.drop_table('announcements')
    op.drop_table('users')
