from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'diko_super_secret_key_change_me'

# --- ФУНКЦИИ РАБОТЫ С БАЗОЙ ДАННЫХ ---
def get_db_connection():
    conn = sqlite3.connect('database/diko.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    if not os.path.exists('database'):
        os.makedirs('database')
    conn = get_db_connection()
    with open('database/schema.sql', 'r', encoding='utf-8') as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()

# --- ГЛАВНАЯ СТРАНИЦА (ПОСТЫ И ЛЕНТА) ---
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
        return jsonify({'error': 'Необходимо авторизоваться'}), 401
    
    data = request.get_json()
    content = data.get('content', '').strip()
    
    if not content:
        return jsonify({'error': 'Текст поста не может быть пустым'}), 400

    conn = get_db_connection()
    conn.execute(
        'INSERT INTO posts (author_id, content, category) VALUES (?, ?, ?)',
        (session['user_id'], content, 'Специализированный пост')
    )
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Пост успешно сохранен в базу данных!'})

# --- АВТОРИЗАЦИЯ И РЕГИСТРАЦИЯ ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        
        if not username or not password:
            return "Пожалуйста, заполните все поля!", 400

        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        try:
            conn.execute(
                'INSERT INTO users (username, password) VALUES (?, ?)',
                (username, hashed_password)
            )
            conn.commit()
        except sqlite3.IntegrityError:
            return "Пользователь с таким именем уже существует!", 400
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
        user = conn.execute(
            'SELECT * FROM users WHERE username = ?', (username,)
        ).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('index'))
        
        return "Неверное имя пользователя или пароль!", 401

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --- ЦЕНТР ПЕРЕПИСОК (ЧАТЫ) ---
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
        return jsonify({'error': 'Сообщение не может быть пустым'}), 400
        
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO messages (chat_id, sender_id, content) VALUES (?, ?, ?)',
        (chat_id, session['user_id'], content)
    )
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'content': content, 'username': session['username']})

# --- ЦЕНТР СОХРАНЕНИЯ: АРХИВ ПЕРЕПИСОК ---
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

# --- ЗАПУСК ПРИЛОЖЕНИЯ ---
if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
