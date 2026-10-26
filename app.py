from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3
import os
import traceback
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'diko_super_secret_key_change_me'
app.config['DEBUG'] = True

DATABASE_PATH = 'database/diko.db'

# --- АВТОМАТИЧЕСКАЯ ИНИЦИАЛИЗАЦИЯ И ОБНОВЛЕНИЕ БАЗЫ ДАННЫХ ---
def init_db():
    try:
        if not os.path.exists('database'):
            os.makedirs('database')

        conn = sqlite3.connect(DATABASE_PATH)
        
        # Встроенная схема со всеми таблицами (безопасна для существующих баз)
        schema_script = """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(50) NOT NULL UNIQUE,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            author_id INTEGER,
            content TEXT NOT NULL,
            category VARCHAR(50) DEFAULT 'Специализированный пост',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(author_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title VARCHAR(100) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS chat_members (
            chat_id INTEGER,
            user_id INTEGER,
            FOREIGN KEY(chat_id) REFERENCES chats(id),
            FOREIGN KEY(user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER,
            sender_id INTEGER,
            content TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(chat_id) REFERENCES chats(id),
            FOREIGN KEY(sender_id) REFERENCES users(id)
        );
        """
        
        conn.executescript(schema_script)
        conn.commit()
        conn.close()
        print("✅ [УСПЕХ]: База данных проверена, все таблицы на месте!")
    except Exception as e:
        print(f"❌ [ОШИБКА ИНИЦИАЛИЗАЦИИ БД]: {e}")

def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# --- ГЛОБАЛЬНЫЙ ПЕРЕХВАТЧИК ОШИБОК (ДИАГНОСТИКА) ---
@app.errorhandler(Exception)
def handle_exception(e):
    print("="*50)
    print("❌ ОШИБКА В СЕРВЕРНОМ КОДЕ:")
    traceback.print_exc()
    print("="*50)
    error_details = traceback.format_exc()
    return f"""
    <div style="font-family: Arial, sans-serif; padding: 20px; background: #121212; color: #ff5555; border-radius: 8px; margin: 20px;">
        <h2>⚠️ Ошибка приложения Diko Messenger</h2>
        <pre style="background: #1e1e1e; color: #ff8888; padding: 15px; border-radius: 5px; overflow-x: auto;">{error_details}</pre>
    </div>
    """, 500

# --- МАРШРУТЫ ПРИЛОЖЕНИЯ ---

@app.route('/')
def index():
    conn = get_db_connection()
    posts = conn.execute('''
        SELECT posts.*, users.username 
        FROM posts 
        JOIN users ON posts.author_id = users.id 
        ORDER BY posts.created_at DESC
    ''').fetchall()
    conn.close()
    return render_template('index.html', posts=posts)

@app.route('/api/posts', methods=['POST'])
def create_post():
    if 'user_id' not in session:
        return jsonify({'error': 'Необходима авторизация'}), 401
    
    data = request.get_json()
    content = data.get('content', '').strip()
    if not content:
        return jsonify({'error': 'Текст пустой'}), 400

    conn = get_db_connection()
    conn.execute(
        'INSERT INTO posts (author_id, content, category) VALUES (?, ?, ?)',
        (session['user_id'], content, 'Специализированный пост')
    )
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        if not username or not password:
            return "Заполните все поля", 400

        hashed_password = generate_password_hash(password)
        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
            conn.commit()
        except sqlite3.IntegrityError:
            return "Пользователь уже существует", 400
        finally:
            conn.close()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('index'))
        return "Неверный логин или пароль", 401
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/chats')
def chats_page():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    user_chats = conn.execute('''
        SELECT chats.* FROM chats
        JOIN chat_members ON chats.id = chat_members.chat_id
        WHERE chat_members.user_id = ?
    ''', (session['user_id'],)).fetchall()
    conn.close()
    return render_template('chats.html', chats=user_chats)

@app.route('/chats/<int:chat_id>')
def view_chat(chat_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    chat = conn.execute('SELECT * FROM chats WHERE id = ?', (chat_id,)).fetchone()
    messages = conn.execute('''
        SELECT messages.*, users.username 
        FROM messages 
        JOIN users ON messages.sender_id = users.id 
        WHERE messages.chat_id = ? 
        ORDER BY messages.timestamp ASC
    ''', (chat_id,)).fetchall()
    conn.close()
    return render_template('chat_room.html', chat=chat, messages=messages)

@app.route('/api/chats/<int:chat_id>/send', methods=['POST'])
def send_chat_message(chat_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Необходима авторизация'}), 401
    data = request.get_json()
    content = data.get('content', '').strip()
    if not content:
        return jsonify({'error': 'Пустое сообщение'}), 400
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO messages (chat_id, sender_id, content) VALUES (?, ?, ?)',
        (chat_id, session['user_id'], content)
    )
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'content': content, 'username': session['username']})

@app.route('/archive')
def archive_page():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    archived_messages = conn.execute('''
        SELECT messages.*, users.username, chats.title as chat_title
        FROM messages 
        JOIN users ON messages.sender_id = users.id 
        JOIN chats ON messages.chat_id = chats.id
        ORDER BY messages.timestamp DESC
    ''').fetchall()
    conn.close()
    return render_template('archive.html', messages=archived_messages)

# --- ЗАПУСК СЕРВЕРА ---
if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
