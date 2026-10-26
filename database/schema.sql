-- Таблиця чатів (діалогів)
CREATE TABLE IF NOT EXISTS chats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблиця учасників чату
CREATE TABLE IF NOT EXISTS chat_members (
    chat_id INTEGER,
    user_id INTEGER,
    FOREIGN KEY(chat_id) REFERENCES chats(id),
    FOREIGN KEY(user_id) REFERENCES users(id)
);

-- Таблиця повідомлень у чатах (Центр переписок)
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id INTEGER,
    sender_id INTEGER,
    content TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(chat_id) REFERENCES chats(id),
    FOREIGN KEY(sender_id) REFERENCES users(id)
);
