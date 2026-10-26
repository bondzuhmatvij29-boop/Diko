-- Таблица пользователей
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    password TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица для специализированных постов на главной странице
CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    author_id INTEGER,
    content TEXT NOT NULL,
    category VARCHAR(50) DEFAULT 'Специализированный пост',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(author_id) REFERENCES users(id)
);

-- Таблица чатов (диалогов)
CREATE TABLE IF NOT EXISTS chats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица участников чата
CREATE TABLE IF NOT EXISTS chat_members (
    chat_id INTEGER,
    user_id INTEGER,
    FOREIGN KEY(chat_id) REFERENCES chats(id),
    FOREIGN KEY(user_id) REFERENCES users(id)
);

-- Таблица сообщений в чатах (Центр переписок)
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id INTEGER,
    sender_id INTEGER,
    content TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(chat_id) REFERENCES chats(id),
    FOREIGN KEY(sender_id) REFERENCES users(id)
);
