from flask import Blueprint, request, render_template, redirect, session, current_app
lab5 = Blueprint('lab5', __name__)
import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3
from os import path

@lab5.route('/lab5/')
def lab():
    return render_template('lab5/lab5.html', login=session.get('login'))

def db_connect():
    if current_app.config['DB_TYPE'] == 'postgres':
        conn = psycopg2.connect(
                host = '127.0.0.1',
                database = 'knowledge_base_df',  
                user='obedina_ekaterina_knowledge_base',
                password='123'
            )
        cur = conn.cursor(cursor_factory= RealDictCursor)
    else:
        dir_path = path.dirname(path.realpath(__file__))
        db_path = path.join(dir_path, "database.db")
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

    return conn, cur

def db_close(conn, cur):
    conn.commit()
    cur.close()
    conn.close()

@lab5.route('/lab5/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('lab5/register.html')
    
    login = request.form.get('login')
    password = request.form.get('password')

    if not login or not password:
        return render_template('lab5/register.html', error='Заполните все поля')
    
    try:
        conn, cur = db_connect()
        
        if current_app.config['DB_TYPE'] == 'postgres':
            cur.execute("SELECT login FROM users WHERE login = %s;", (login,))
        else:
            cur.execute("SELECT login FROM users WHERE login = ?;", (login,))
        if cur.fetchone():
            db_close(conn, cur)
            return render_template('lab5/register.html', error="Такой пользователь уже существует")

        hashed_password = generate_password_hash(password)
        
        if current_app.config['DB_TYPE'] == 'postgres':
            cur.execute("INSERT INTO users (login, password) VALUES (%s, %s)", 
                       (login, hashed_password))
        else:
            cur.execute("INSERT INTO users (login, password) VALUES (?, ?)", 
                       (login, hashed_password))
        
        db_close(conn, cur)
        return render_template('lab5/success.html', login=login)
        
    except Exception as e:
        return render_template('lab5/register.html', error=f'Ошибка базы данных: {str(e)}')

@lab5.route('/lab5/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('lab5/login.html')
    
    login = request.form.get('login')
    password = request.form.get('password')

    if not login or not password:
        return render_template('lab5/login.html', error="Заполните поля")
    
    try:
        conn, cur = db_connect()
        
        if current_app.config['DB_TYPE'] == 'postgres':
            cur.execute("SELECT * FROM users WHERE login = %s;", (login,))
        else:
            cur.execute("SELECT * FROM users WHERE login = ?;", (login,))
        user = cur.fetchone()

        if not user:
            db_close(conn, cur)
            return render_template('lab5/login.html', error='Логин и/или пароль неверны')
        
        if not check_password_hash(user['password'], password):
            db_close(conn, cur)
            return render_template('lab5/login.html', error='Логин и/или пароль неверны')
        
        session['user_login'] = login
        session['user_id'] = user['id']  # Сохраняем ID пользователя в сессии
        
        db_close(conn, cur)
        return render_template('lab5/success_login.html', login=login)

    except Exception as e:
        return render_template('lab5/login.html', error=f'Ошибка базы данных: {str(e)}')

@lab5.route('/lab5/logout')
def logout():
    session.pop('user_login', None)
    session.pop('user_id', None)
    return redirect('/lab5')

@lab5.route('/lab5/create', methods = ['GET', 'POST'])
def create():
    login = session.get('user_login')
    if not login:
        return redirect('/lab5/login')
    
    if request.method == 'GET':
        return render_template('lab5/create_article.html')
    
    title = request.form.get('title')
    article_text = request.form.get('article_text')

    if not title or not article_text:
        return render_template('lab5/create_article.html', error='Заполните все поля')

    try:
        conn, cur = db_connect()

        # Способ 1: Используем ID пользователя из сессии (более надежно)
        user_id = session.get('user_id')
        
        if user_id:
            # Если ID пользователя есть в сессии, используем его
            login_id = user_id
            print(f"Используем user_id из сессии: {login_id}")
        else:
            # Способ 2: Получаем ID пользователя из базы данных
            if current_app.config['DB_TYPE'] == 'postgres':
                cur.execute("SELECT id FROM users WHERE login = %s;", (login,))
            else:
                cur.execute("SELECT id FROM users WHERE login = ?;", (login,))
            user = cur.fetchone()
            
            if not user:
                db_close(conn, cur)
                return render_template('lab5/create_article.html', error="Пользователь не найден")
            
            login_id = user["id"]
            print(f"Получили user_id из базы: {login_id}")

        # Отладочная информация
        print(f"Создание статьи: login_id={login_id}, title='{title}', article_text='{article_text[:50]}...'")

        # Вставляем статью с правильным login_id
        if current_app.config['DB_TYPE'] == 'postgres':
            cur.execute("INSERT INTO articles (login_id, title, article_text) VALUES (%s, %s, %s);", 
                       (login_id, title, article_text))
        else:
            cur.execute("INSERT INTO articles (login_id, title, article_text) VALUES (?, ?, ?);", 
                       (login_id, title, article_text))
        
        db_close(conn, cur)
        return redirect('/lab5')
    
    except Exception as e:
        print(f"Ошибка при создании статьи: {str(e)}")
        return render_template('lab5/create_article.html', error=f'Ошибка при создании статьи: {str(e)}')

@lab5.route('/lab5/list')
def list_articles():
    login = session.get('user_login')
    if not login:
        return redirect('/lab5/login')
    
    try:
        conn, cur = db_connect()

        # Используем ID из сессии или получаем из базы
        user_id = session.get('user_id')
        if not user_id:
            if current_app.config['DB_TYPE'] == 'postgres':
                cur.execute("SELECT id FROM users WHERE login = %s;", (login,))
            else:
                cur.execute("SELECT id FROM users WHERE login = ?;", (login,))
            user = cur.fetchone()
            
            if not user:
                db_close(conn, cur)
                return redirect('/lab5/login')
            
            user_id = user["id"]

        # Получаем статьи пользователя
        if current_app.config['DB_TYPE'] == 'postgres':
            cur.execute("SELECT * FROM articles WHERE login_id = %s;", (user_id,))
        else:
            cur.execute("SELECT * FROM articles WHERE login_id = ?;", (user_id,))
        articles = cur.fetchall()

        db_close(conn, cur)
        return render_template('lab5/articles.html', articles=articles)
    
    except Exception as e:
        print(f"Ошибка в list_articles: {str(e)}")
        return render_template('lab5/articles.html', articles=[], error=f"Ошибка при загрузке статей: {str(e)}")