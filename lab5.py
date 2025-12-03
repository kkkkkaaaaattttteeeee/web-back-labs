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
    full_name = request.form.get('full_name', '').strip()

    if not login or not password:
        return render_template('lab5/register.html', error='Заполните все обязательные поля')
    
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
            cur.execute("INSERT INTO users (login, password, full_name) VALUES (%s, %s, %s)", 
                       (login, hashed_password, full_name))
        else:
            cur.execute("INSERT INTO users (login, password, full_name) VALUES (?, ?, ?)", 
                       (login, hashed_password, full_name))
        
        # После успешной регистрации
        # Авторизуем пользователя сразу же
        session['user_login'] = login
        # Получаем ID нового пользователя
        if current_app.config['DB_TYPE'] == 'postgres':
            cur.execute("SELECT id FROM users WHERE login = %s;", (login,))
            user_id = cur.fetchone()['id']
        else:
            cur.execute("SELECT id FROM users WHERE login = ?;", (login,))
            user_id = cur.fetchone()['id']
        
        session['user_id'] = user_id
        session['user_full_name'] = full_name
        
        db_close(conn, cur)
        
        # После регистрации остаемся в lab5 (не переходим на lab6)
        return render_template('lab5/success.html', login=login)
        
    except Exception as e:
        return render_template('lab5/register.html', error=f'Ошибка базы данных: {str(e)}')

@lab5.route('/lab5/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('lab5/login.html', next=request.args.get('next'))
    
    login = request.form.get('login')
    password = request.form.get('password')
    next_page = request.form.get('next')  # Получаем next из формы

    if not login or not password:
        return render_template('lab5/login.html', error="Заполните все поля", next=next_page)
    
    try:
        conn, cur = db_connect()
        
        if current_app.config['DB_TYPE'] == 'postgres':
            cur.execute("SELECT * FROM users WHERE login = %s;", (login,))
        else:
            cur.execute("SELECT * FROM users WHERE login = ?;", (login,))
        user_row = cur.fetchone()

        if not user_row:
            db_close(conn, cur)
            return render_template('lab5/login.html', error='Логин и/или пароль неверны', next=next_page)

        user = convert_to_dict(user_row)
        
        if not check_password_hash(user['password'], password):
            db_close(conn, cur)
            return render_template('lab5/login.html', error='Логин и/или пароль неверны', next=next_page)
        
        session['user_login'] = login
        session['user_id'] = user['id']
        session['user_full_name'] = user.get('full_name', '')
        
        db_close(conn, cur)

        # Логика перенаправления:
        # 1. Если есть next_page (пришел с lab6) - перебрасываем туда
        # 2. Если нет next_page (пришел из lab5) - остаемся в lab5
        if next_page:
            return redirect(next_page)
        else:
            return render_template('lab5/success_login.html', login=login)

    except Exception as e:
        return render_template('lab5/login.html', error=f'Ошибка базы данных: {str(e)}', next=next_page)

@lab5.route('/lab5/logout')
def logout():
    # Получаем параметр next из запроса
    next_page = request.args.get('next', '/lab5/')
    
    # Очищаем сессию
    session.pop('user_login', None)
    session.pop('user_id', None)
    session.pop('user_full_name', None)
    flash('Вы успешно вышли из системы', 'success')
    
    # Перенаправляем на указанную страницу
    return redirect(next_page)

@lab5.route('/lab5/create', methods = ['GET', 'POST'])
def create():
    login = session.get('user_login')
    if not login:
        return redirect('/lab5/login')
    
    if request.method == 'GET':
        return render_template('lab5/create_article.html')
    
    title = request.form.get('title', '').strip()
    article_text = request.form.get('article_text', '').strip()
    is_favorite = bool(request.form.get('is_favorite'))
    is_public = bool(request.form.get('is_public'))

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
            cur.execute("INSERT INTO articles (user_id, title, article_text, is_favorite, is_public) VALUES (%s, %s, %s, %s, %s);", 
                       (user_id, title, article_text, is_favorite, is_public))
        else:
            cur.execute("INSERT INTO articles (login_id, title, article_text, is_favorite, is_public) VALUES (?, ?, ?, ?, ?);", 
                       (user_id, title, article_text, is_favorite, is_public))
        
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
        is_favorite = bool(request.form.get('is_favorite'))
        is_public = bool(request.form.get('is_public'))

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
            cur.execute("UPDATE articles SET title = %s, article_text = %s, is_favorite = %s, is_public = %s WHERE id = %s;", 
                       (title, article_text, is_favorite, is_public, article_id))
        else:
            cur.execute("UPDATE articles SET title = ?, article_text = ?, is_favorite = ?, is_public = ? WHERE id = ?;", 
                       (title, article_text, is_favorite, is_public, article_id))
        
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
        # Сортируем по is_favorite - любимые статьи первыми
        if current_app.config['DB_TYPE'] == 'postgres':
            cur.execute("SELECT * FROM articles WHERE user_id = %s ORDER BY is_favorite DESC, id DESC;", (user_id,))
        else:
            cur.execute("SELECT * FROM articles WHERE login_id = ? ORDER BY is_favorite DESC, id DESC;", (user_id,))
        
        articles_rows = cur.fetchall()
        
        # Конвертируем все строки в словари для универсального доступа в шаблоне
        articles = [convert_to_dict(article) for article in articles_rows]
        
        db_close(conn, cur)
        return render_template('lab5/articles.html', articles=articles)
    
    except Exception as e:
        print(f"Ошибка в list_articles: {str(e)}")
        return render_template('lab5/articles.html', articles=[], error=f'Ошибка при загрузке статей: {str(e)}')

@lab5.route('/lab5/public')
def public_articles():
    """Публичные статьи для всех пользователей"""
    try:

        conn, cur = db_connect()

        # Получаем все публичные статьи с информацией об авторах
        if current_app.config['DB_TYPE'] == 'postgres':
            cur.execute("""
                SELECT a.*, u.login as author_login, u.full_name as author_name 
                FROM articles a 
                JOIN users u ON a.user_id = u.id 
                WHERE a.is_public = true 
                ORDER BY a.is_favorite DESC, a.id DESC;
            """)
        else:
            cur.execute("""
                SELECT a.*, u.login as author_login, u.full_name as author_name 
                FROM articles a 
                JOIN users u ON a.login_id = u.id 
                WHERE a.is_public = 1 
                ORDER BY a.is_favorite DESC, a.id DESC;
            """)
        
        articles_rows = cur.fetchall()
        articles = [convert_to_dict(article) for article in articles_rows]
        
        db_close(conn, cur)
        return render_template('lab5/public_articles.html', articles=articles)
    
    except Exception as e:
        print(f"Ошибка в public_articles: {str(e)}")
        return render_template('lab5/public_articles.html', articles=[], error=f'Ошибка при загрузке публичных статей: {str(e)}')

@lab5.route('/lab5/users')
def users_list():
    """Список всех пользователей"""
    try:
        conn, cur = db_connect()

        # Сортируем по логину для алфавитного порядка
        if current_app.config['DB_TYPE'] == 'postgres':
            cur.execute("SELECT id, login, full_name FROM users ORDER BY login;")
        else:
            cur.execute("SELECT id, login, full_name FROM users ORDER BY login;")
        
        users_rows = cur.fetchall()
        users = [convert_to_dict(user) for user in users_rows]
        
        db_close(conn, cur)
        return render_template('lab5/users.html', users=users)
    
    except Exception as e:
        print(f"Ошибка в users_list: {str(e)}")
        return render_template('lab5/users.html', users=[], error=f'Ошибка при загрузке пользователей: {str(e)}')

@lab5.route('/lab5/profile', methods=['GET', 'POST'])
def profile():
    """Страница смены имени и пароля"""
    login = session.get('user_login')
    if not login:
        return redirect('/lab5/login')
    
    if request.method == 'GET':
        return render_template('lab5/profile.html')
    
    # Обработка формы
    full_name = request.form.get('full_name', '').strip()
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    try:
        conn, cur = db_connect()
        user_id = session.get('user_id')

        # Получаем текущие данные пользователя
        if current_app.config['DB_TYPE'] == 'postgres':
            cur.execute("SELECT * FROM users WHERE id = %s;", (user_id,))
        else:
            cur.execute("SELECT * FROM users WHERE id = ?;", (user_id,))
        
        user_row = cur.fetchone()
        user = convert_to_dict(user_row)
        
        changes_made = False
        
        # Обновляем полное имя, если оно изменилось
        if full_name != user.get('full_name', ''):
            if current_app.config['DB_TYPE'] == 'postgres':
                cur.execute("UPDATE users SET full_name = %s WHERE id = %s;", (full_name, user_id))
            else:
                cur.execute("UPDATE users SET full_name = ? WHERE id = ?;", (full_name, user_id))
            changes_made = True
            session['user_full_name'] = full_name
        
        # Обновляем пароль, если введены все необходимые поля
        if current_password and new_password and confirm_password:
            # Проверяем текущий пароль
            if not check_password_hash(user['password'], current_password):
                db_close(conn, cur)
                return render_template('lab5/profile.html', error='Текущий пароль неверен')
            
            # Проверяем совпадение нового пароля и подтверждения
            if new_password != confirm_password:
                db_close(conn, cur)
                return render_template('lab5/profile.html', error='Новый пароль и подтверждение не совпадают')
            
            # Проверяем длину нового пароля
            if len(new_password) < 4:
                db_close(conn, cur)
                return render_template('lab5/profile.html', error='Новый пароль должен содержать минимум 4 символа')
            
            # Хэшируем и обновляем пароль
            hashed_new_password = generate_password_hash(new_password)
            if current_app.config['DB_TYPE'] == 'postgres':
                cur.execute("UPDATE users SET password = %s WHERE id = %s;", (hashed_new_password, user_id))
            else:
                cur.execute("UPDATE users SET password = ? WHERE id = ?;", (hashed_new_password, user_id))
            changes_made = True
        
        db_close(conn, cur)
        
        if changes_made:
            flash('Профиль успешно обновлен!', 'success')
        else:
            flash('Изменений не внесено', 'info')
        
        return redirect('/lab5/profile')
    
    except Exception as e:
        return render_template('lab5/profile.html', error=f'Ошибка при обновлении профиля: {str(e)}')