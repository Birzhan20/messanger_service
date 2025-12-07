"""
CREATE TABLE IF NOT EXISTS chats (
    id BIGSERIAL PRIMARY KEY,

    announcement_id BIGINT NOT NULL,
    seller_id       BIGINT NOT NULL,
    buyer_id        BIGINT NOT NULL,

    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW(),
    last_message_text   VARCHAR(255),
    last_message_type   VARCHAR(20) DEFAULT 'text',
    last_message_at     TIMESTAMP NULL,

    -- Связи
    CONSTRAINT fk_chats_announcement
        FOREIGN KEY (announcement_id) REFERENCES announcements(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_chats_seller
        FOREIGN KEY (seller_id) REFERENCES users(id),

    CONSTRAINT fk_chats_buyer
        FOREIGN KEY (buyer_id) REFERENCES users(id),

    -- ГЛАВНОЕ: один чат = одно объявление + один продавец + один покупатель
    CONSTRAINT uq_chat_unique
        UNIQUE (announcement_id, seller_id, buyer_id)
);

-- CREATE TABLE IF NOT EXISTS messages (
--     id BIGSERIAL PRIMARY KEY,
--     chat_id BIGINT NOT NULL,
--     sender_id BIGINT NOT NULL,
--     message_text TEXT,
--     message_type VARCHAR(20) DEFAULT 'text',
--     file_url VARCHAR(500),
--     is_read BOOLEAN DEFAULT FALSE,
--     created_at TIMESTAMP DEFAULT NOW(),
--
--     CONSTRAINT fk_messages_chat
--         FOREIGN KEY (chat_id) REFERENCES chats(id),
--
--     CONSTRAINT fk_messages_sender
--         FOREIGN KEY (sender_id) REFERENCES users(id)
-- );
"""