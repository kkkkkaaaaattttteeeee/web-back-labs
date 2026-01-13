from flask import Blueprint, render_template, request, redirect
from db import db
from db.models import users, articles
from flask_login import login_user, login_required, current_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy import or_

lab8 = Blueprint('lab8', __name__, template_folder='templates/lab8')

@lab8.route('/lab8/')
def index():
    return render_template('lab8/lab8.html')

@lab8.route('/lab8/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('lab8/login.html')
    
    login_form = request.form.get('login')
    password_form = request.form.get('password')
    remember = request.form.get('remember')

    if not login_form or not password_form:
        return render_template('lab8/login.html', 
                               error='Логин и пароль не могут быть пустыми')
    
    user = users.query.filter_by(login=login_form).first()

    if user:
        if check_password_hash(user.password, password_form):
            login_user(user, remember=bool(remember))
            return redirect('/lab8/')
    
    return render_template('lab8/login.html',
                           error='Ошибка входа: логин и/или пароль неверны')

@lab8.route('/lab8/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('lab8/register.html')

    login_form = request.form.get('login')
    password_form = request.form.get('password')
    
    if not login_form or not password_form:
        return render_template('lab8/register.html', 
                               error='Логин и пароль не могут быть пустыми')
    
    login_exists = users.query.filter_by(login=login_form).first()

    if login_exists:
        return render_template('lab8/register.html',
                               error='Такой пользователь уже существует')
    
    password_hash = generate_password_hash(password_form)
    new_user = users(login=login_form, password=password_hash)
    
    db.session.add(new_user)
    db.session.commit()
    
    login_user(new_user, remember=False)
    return redirect('/lab8/')

@lab8.route('/lab8/articles')
@login_required
def articles_list():
    try:
        user_articles = articles.query.filter_by(login_id=current_user.id).all()
    except:
        user_articles = []
    
    return render_template('lab8/articles.html', 
                           title="Мои статьи",
                           articles=user_articles)

# 1. Реализуйте вывод публичных статей (is_public) для всех пользователей
@lab8.route('/lab8/articles/public')
def public_articles():
    """
    Отображает все публичные статьи (доступно всем).
    """
    try:
        # Получаем только публичные статьи
        public_articles_list = articles.query.filter_by(is_public=True).all()
    except Exception as e:
        print(f"Ошибка при получении публичных статей: {e}")
        public_articles_list = []
    
    # Получаем имена авторов для отображения
    articles_with_authors = []
    for article in public_articles_list:
        try:
            author = users.query.get(article.login_id)
            article.author_name = author.login if author else "Неизвестный автор"
            articles_with_authors.append(article)
        except:
            article.author_name = "Неизвестный автор"
            articles_with_authors.append(article)
    
    return render_template('lab8/public_articles.html', 
                           title="Публичные статьи",
                           articles=articles_with_authors)

# 2. Реализуйте поиск по статьям (регистронезависимый)
@lab8.route('/lab8/articles/search', methods=['GET', 'POST'])
def search_articles():
    """
    Поиск по статьям (регистронезависимый).
    Доступен всем пользователям.
    """
    if request.method == 'GET':
        return render_template('lab8/search.html', 
                               title="Поиск статей")
    
    search_query = request.form.get('search_query', '').strip()
    
    if not search_query:
        return render_template('lab8/search.html', 
                               error="Введите поисковый запрос")
    
    try:
        search_pattern = f"%{search_query}%"
        
        # Если пользователь авторизован
        if current_user.is_authenticated:
            # Ищем в своих статьях (любых) + публичных статьях других пользователей
            search_results = articles.query.filter(
                db.or_(
                    # Свои статьи (любые)
                    db.and_(
                        articles.login_id == current_user.id,
                        db.or_(
                            articles.title.ilike(search_pattern),
                            articles.article_text.ilike(search_pattern)
                        )
                    ),
                    # Публичные статьи других пользователей
                    db.and_(
                        articles.login_id != current_user.id,
                        articles.is_public == True,
                        db.or_(
                            articles.title.ilike(search_pattern),
                            articles.article_text.ilike(search_pattern)
                        )
                    )
                )
            ).all()
        else:
            # Для неавторизованных - только публичные статьи
            search_results = articles.query.filter(
                articles.is_public == True,
                db.or_(
                    articles.title.ilike(search_pattern),
                    articles.article_text.ilike(search_pattern)
                )
            ).all()
        
        # Получаем имена авторов для отображения
        results_with_authors = []
        for article in search_results:
            try:
                author = users.query.get(article.login_id)
                article.author_name = author.login if author else "Неизвестный автор"
                article.is_owner = (current_user.is_authenticated and 
                                   article.login_id == current_user.id)
                results_with_authors.append(article)
            except:
                article.author_name = "Неизвестный автор"
                article.is_owner = False
                results_with_authors.append(article)
        
        return render_template('lab8/search_results.html', 
                               title="Результаты поиска",
                               articles=results_with_authors, 
                               search_query=search_query,
                               results_count=len(results_with_authors))
        
    except Exception as e:
        print(f"Ошибка при поиске: {e}")
        return render_template('lab8/search.html', 
                               error=f"Ошибка при поиске: {str(e)}")

@lab8.route('/lab8/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'GET':
        return render_template('lab8/create.html', title="Создать статью")
    
    title = request.form.get('title')
    article_text = request.form.get('article_text')
    is_public = request.form.get('is_public')
    
    if not title or not article_text:
        return render_template('lab8/create.html',
                               error='Заголовок и текст статьи обязательны')
    
    try:
        new_article = articles(
            login_id=current_user.id,
            title=title,
            article_text=article_text,
            is_favorite=False,
            is_public=(is_public == '1'),
            likes=0
        )
        
        db.session.add(new_article)
        db.session.commit()
        
        return redirect('/lab8/articles')
    except Exception as e:
        print(f"Ошибка при создании: {e}")
        return render_template('lab8/create.html',
                               error=f'Ошибка при создании: {str(e)}')

@lab8.route('/lab8/edit/<int:article_id>', methods=['GET', 'POST'])
@login_required
def edit(article_id):
    try:
        article = articles.query.filter_by(id=article_id, login_id=current_user.id).first()
    except:
        article = None
    
    if not article:
        return redirect('/lab8/articles')
    
    if request.method == 'GET':
        return render_template('lab8/edit.html',
                               title="Редактировать статью",
                               article=article)
    
    article.title = request.form.get('title')
    article.article_text = request.form.get('article_text')
    article.is_public = (request.form.get('is_public') == '1')
    
    if not article.title or not article.article_text:
        return render_template('lab8/edit.html',
                               error='Заголовок и текст статьи обязательны',
                               article=article)
    
    try:
        db.session.commit()
        return redirect('/lab8/articles')
    except Exception as e:
        return render_template('lab8/edit.html',
                               error=f'Ошибка при сохранении: {str(e)}',
                               article=article)

@lab8.route('/lab8/delete/<int:article_id>', methods=['POST'])
@login_required
def delete(article_id):
    try:
        article = articles.query.filter_by(id=article_id, login_id=current_user.id).first()
        if article:
            db.session.delete(article)
            db.session.commit()
    except:
        pass
    
    return redirect('/lab8/articles')

@lab8.route('/lab8/logout')
@login_required
def logout():
    logout_user()
    return redirect('/lab8/')