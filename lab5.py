from flask import Blueprint, request, render_template, redirect, session, current_app, flash
lab5 = Blueprint('lab5', __name__)
import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3
from os import path

@lab5.route('/lab5/')
def lab():
    return render_template('lab5/lab5.html', login=session.get('user_login'))

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

def convert_to_dict(obj):
    """Конвертирует объект строки в словарь для универсального доступа"""
    if obj is None:
        return None
    if hasattr(obj, '_asdict'):  # Для namedtuple
        return obj._asdict()
    elif hasattr(obj, 'keys'):  # Для словарей и подобных
        return dict(obj)
    else:  # Для sqlite3.Row и других
        return dict(obj)

@lab5.route('/lab5/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('lab5/register.html')
    
    login = request.form.get('login')
    password = request.form.get('password')

    if not login or not password:
        return render_template('lab5/register.html', error='Заполните все поля')
    
    if len(login) < 3:
        return render_template('lab5/register.html', error='Логин должен содержать минимум 3 символа')
    
    if len(password) < 4:
        return render_template('lab5/register.html', error='Пароль должен содержать минимум 4 символа')
    
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
        return render_template('lab5/login.html', error="Заполните все поля")
    
    try:
        conn, cur = db_connect()
        
        if current_app.config['DB_TYPE'] == 'postgres':
            cur.execute("SELECT * FROM users WHERE login = %s;", (login,))
        else:
            cur.execute("SELECT * FROM users WHERE login = ?;", (login,))
        user_row = cur.fetchone()

        if not user_row:
            db_close(conn, cur)
            return render_template('lab5/login.html', error='Логин и/или пароль неверны')
        
        # Конвертируем в словарь для универсального доступа
        user = convert_to_dict(user_row)
        
        if not check_password_hash(user['password'], password):
            db_close(conn, cur)
            return render_template('lab5/login.html', error='Логин и/или пароль неверны')
        
        session['user_login'] = login
        session['user_id'] = user['id']
        
        db_close(conn, cur)
        return render_template('lab5/success_login.html', login=login)

    except Exception as e:
        return render_template('lab5/login.html', error=f'Ошибка базы данных: {str(e)}')

@lab5.route('/lab5/logout')
def logout():
    session.pop('user_login', None)
    session.pop('user_id', None)
    flash('Вы успешно вышли из системы', 'success')
    return redirect('/lab5')

@lab5.route('/lab5/create', methods = ['GET', 'POST'])
def create():
    login = session.get('user_login')
    if not login:
        return redirect('/lab5/login')
    
    if request.method == 'GET':
        return render_template('lab5/create_article.html')
    
    title = request.form.get('title', '').strip()
    article_text = request.form.get('article_text', '').strip()

    if not title:
        return render_template('lab5/create_article.html', error='Введите название статьи')
    
    if not article_text:
        return render_template('lab5/create_article.html', error='Введите текст статьи')
    
    if len(title) > 50:
        return render_template('lab5/create_article.html', error='Название статьи не должно превышать 50 символов')

    try:
        conn, cur = db_connect()
        user_id = session.get('user_id')

        # Для PostgreSQL используем user_id, для SQLite используем login_id
        if current_app.config['DB_TYPE'] == 'postgres':
            cur.execute("INSERT INTO articles (user_id, title, article_text) VALUES (%s, %s, %s);", 
                       (user_id, title, article_text))
        else:
            cur.execute("INSERT INTO articles (login_id, title, article_text) VALUES (?, ?, ?);", 
                       (user_id, title, article_text))
        
        db_close(conn, cur)
        flash('Статья успешно создана!', 'success')
        return redirect('/lab5/list')
    
    except Exception as e:
        print(f"Ошибка при создании статьи: {str(e)}")
        return render_template('lab5/create_article.html', error=f'Ошибка при создании статьи: {str(e)}')

@lab5.route('/lab5/edit/<int:article_id>', methods=['GET', 'POST'])
def edit_article(article_id):
    login = session.get('user_login')
    if not login:
        return redirect('/lab5/login')
    
    try:
        conn, cur = db_connect()
        user_id = session.get('user_id')

        # Для PostgreSQL используем user_id, для SQLite используем login_id
        if current_app.config['DB_TYPE'] == 'postgres':
            cur.execute("SELECT * FROM articles WHERE id = %s AND user_id = %s;", (article_id, user_id))
        else:
            cur.execute("SELECT * FROM articles WHERE id = ? AND login_id = ?;", (article_id, user_id))
        
        article_row = cur.fetchone()
        
        if not article_row:
            db_close(conn, cur)
            flash('Статья не найдена или у вас нет прав для ее редактирования', 'error')
            return redirect('/lab5/list')

        # Конвертируем в словарь для универсального доступа
        article = convert_to_dict(article_row)

        if request.method == 'GET':
            db_close(conn, cur)
            return render_template('lab5/edit_article.html', article=article)

        # Обработка формы редактирования
        title = request.form.get('title', '').strip()
        article_text = request.form.get('article_text', '').strip()

        if not title:
            db_close(conn, cur)
            return render_template('lab5/edit_article.html', article=article, error='Введите название статьи')
        
        if not article_text:
            db_close(conn, cur)
            return render_template('lab5/edit_article.html', article=article, error='Введите текст статьи')
        
        if len(title) > 50:
            db_close(conn, cur)
            return render_template('lab5/edit_article.html', article=article, error='Название статьи не должно превышать 50 символов')

        # Обновляем статью
        if current_app.config['DB_TYPE'] == 'postgres':
            cur.execute("UPDATE articles SET title = %s, article_text = %s WHERE id = %s;", 
                       (title, article_text, article_id))
        else:
            cur.execute("UPDATE articles SET title = ?, article_text = ? WHERE id = ?;", 
                       (title, article_text, article_id))
        
        db_close(conn, cur)
        flash('Статья успешно обновлена!', 'success')
        return redirect('/lab5/list')
    
    except Exception as e:
        return render_template('lab5/edit_article.html', article=article, error=f'Ошибка при редактировании статьи: {str(e)}')

@lab5.route('/lab5/delete/<int:article_id>')
def delete_article(article_id):
    login = session.get('user_login')
    if not login:
        return redirect('/lab5/login')
    
    try:
        conn, cur = db_connect()
        user_id = session.get('user_id')

        # Для PostgreSQL используем user_id, для SQLite используем login_id
        if current_app.config['DB_TYPE'] == 'postgres':
            cur.execute("SELECT * FROM articles WHERE id = %s AND user_id = %s;", (article_id, user_id))
        else:
            cur.execute("SELECT * FROM articles WHERE id = ? AND login_id = ?;", (article_id, user_id))
        
        article = cur.fetchone()
        
        if not article:
            db_close(conn, cur)
            flash('Статья не найдена или у вас нет прав для ее удаления', 'error')
            return redirect('/lab5/list')

        # Удаляем статью
        if current_app.config['DB_TYPE'] == 'postgres':
            cur.execute("DELETE FROM articles WHERE id = %s;", (article_id,))
        else:
            cur.execute("DELETE FROM articles WHERE id = ?;", (article_id,))
        
        db_close(conn, cur)
        flash('Статья успешно удалена!', 'success')
        return redirect('/lab5/list')
    
    except Exception as e:
        flash(f'Ошибка при удалении статьи: {str(e)}', 'error')
        return redirect('/lab5/list')

@lab5.route('/lab5/list')
def list_articles():
    login = session.get('user_login')
    if not login:
        return redirect('/lab5/login')
    
    try:
        conn, cur = db_connect()
        user_id = session.get('user_id')

        # Для PostgreSQL используем user_id, для SQLite используем login_id
        if current_app.config['DB_TYPE'] == 'postgres':
            cur.execute("SELECT * FROM articles WHERE user_id = %s ORDER BY id DESC;", (user_id,))
        else:
            cur.execute("SELECT * FROM articles WHERE login_id = ? ORDER BY id DESC;", (user_id,))
        
        articles_rows = cur.fetchall()
        
        # Конвертируем все строки в словари для универсального доступа в шаблоне
        articles = [convert_to_dict(article) for article in articles_rows]
        
        db_close(conn, cur)
        return render_template('lab5/articles.html', articles=articles)
    
    except Exception as e:
        print(f"Ошибка в list_articles: {str(e)}")
        return render_template('lab5/articles.html', articles=[], error=f'Ошибка при загрузке статей: {str(e)}')