from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'diko_super_secret_key_change_me'

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

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
