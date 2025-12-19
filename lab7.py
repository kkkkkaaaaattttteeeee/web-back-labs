from flask import Blueprint, request, render_template, jsonify, current_app
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
import sqlite3
from os import path

lab7 = Blueprint('lab7', __name__)

# Глобальная переменная для отслеживания инициализации БД
_db_initialized = False

# Функции для работы с БД
def db_connect():
    """Универсальная функция для подключения к БД"""
    if current_app.config.get('DB_TYPE') == 'postgres':
        conn = psycopg2.connect(
            host='127.0.0.1',
            database='knowledge_base_df',
            user='obedina_ekaterina_knowledge_base',
            password='123'
        )
        cur = conn.cursor(cursor_factory=RealDictCursor)
    else:
        dir_path = path.dirname(path.realpath(__file__))
        db_path = path.join(dir_path, "database.db")
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
    
    return conn, cur

def db_close(conn, cur):
    """Закрытие соединения с БД"""
    conn.commit()
    cur.close()
    conn.close()

def convert_to_dict(obj):
    """Конвертирует объект строки в словарь"""
    if obj is None:
        return None
    if hasattr(obj, '_asdict'):  # Для namedtuple
        return obj._asdict()
    elif hasattr(obj, 'keys'):  # Для словарей
        return dict(obj)
    else:  # Для sqlite3.Row
        return dict(obj)

def init_db():
    """Инициализация БД (создание таблицы, если её нет)"""
    global _db_initialized
    if _db_initialized:
        return
    
    conn, cur = db_connect()
    
    try:
        if current_app.config.get('DB_TYPE') == 'postgres':
            # Создаем таблицу для PostgreSQL
            cur.execute('''
                CREATE TABLE IF NOT EXISTS films (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(500),
                    title_ru VARCHAR(500) NOT NULL,
                    year INTEGER NOT NULL,
                    description TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
        else:
            # Создаем таблицу для SQLite
            cur.execute('''
                CREATE TABLE IF NOT EXISTS films (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    title_ru TEXT NOT NULL,
                    year INTEGER NOT NULL,
                    description TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
        
        # Проверяем, есть ли уже фильмы
        if current_app.config.get('DB_TYPE') == 'postgres':
            cur.execute('SELECT COUNT(*) as count FROM films')
        else:
            cur.execute('SELECT COUNT(*) as count FROM films')
        
        count = cur.fetchone()['count']
        
        if count == 0:
            # Вставляем начальные данные
            initial_films = [
                ("Interstellar", "Интерстеллар", 2014, "Когда засуха, пыльные бури и вымирание растений приводят человечество к продовольственному кризису, коллектив исследователей и учёных отправляется сквозь червоточину (которая предположительно соединяет области пространства времени через большое расстояние) в путешествие, чтобы превзойти прежние ограничения для космических путешествий человека и найти планету с подходящими для человечества условиями."),
                ("The Shawshank Redemption", "Побег из Шоушенка", 1994, "Бухгалтер Энди Дюфрейн обвинён в убийстве собственной жены и её любовника. Оказавшись в тюрьме под названием Шоушенк, он сталкивается с жестокостью и беззаконным, царящими по обе стороны решётки. Каждый, кто попадает в эти стены, становится их рабом до конца жизни. Но Энди, обладающий жилым умом и доброй душой, находит подход как к заключённым, так и к охранникам, добиваясь их особого к себе расположения."),
                ("The Green Mile", "Зеленая миля", 1999, "Пол Эджкомб — начальник блока смертников в тюрьме «Холодная гора». Каждый из узников которого однажды проходит последний путь по зловещей коридорной плитке, отмеченной зелёным линолеумом, в сторону электрического стула. Вскоре к нему поступает необычный заключённый — гигант Джон Коффи, осуждённый за страшное преступление, но обладающий удивительными целительными способностями и детской душой. Эта встреча навсегда изменит жизнь Пола и заставит его задуматься о чудесах, справедливости и смысле наказания.")
            ]
            
            for film in initial_films:
                if current_app.config.get('DB_TYPE') == 'postgres':
                    cur.execute('''
                        INSERT INTO films (title, title_ru, year, description)
                        VALUES (%s, %s, %s, %s)
                    ''', film)
                else:
                    cur.execute('''
                        INSERT INTO films (title, title_ru, year, description)
                        VALUES (?, ?, ?, ?)
                    ''', film)
        
        _db_initialized = True
        db_close(conn, cur)
    except Exception as e:
        print(f"Ошибка при инициализации БД: {str(e)}")
        db_close(conn, cur)

# Добавляем обработчик before_request для инициализации БД перед каждым запросом
@lab7.before_request
def initialize_db():
    """Инициализация БД перед каждым запросом"""
    if not _db_initialized:
        init_db()

def validate_film_data(film):
    """Валидация данных фильма"""
    errors = {}
    
    # Проверка русского названия - должно быть непустым
    if not film.get('title_ru') or film['title_ru'].strip() == '':
        errors['title_ru'] = 'Введите название на русском'
    
    # Проверка оригинального названия - должно быть непустым, если русское пустое
    if (not film.get('title_ru') or film['title_ru'].strip() == '') and (not film.get('title') or film['title'].strip() == ''):
        errors['title'] = 'Введите название на оригинальном языке'
    
    # Проверка года - должен быть от 1895 до текущего
    current_year = datetime.now().year
    if not film.get('year'):
        errors['year'] = 'Введите год выпуска'
    else:
        try:
            year = int(film['year'])
            if year < 1895 or year > current_year:
                errors['year'] = f'Введите корректный год (1895-{current_year})'
        except ValueError:
            errors['year'] = 'Год должен быть числом'
    
    # Проверка описания - должно быть непустым, но не более 2000 символов
    if not film.get('description') or film['description'].strip() == '':
        errors['description'] = 'Заполните описание'
    elif len(film['description']) > 2000:
        errors['description'] = 'Описание не должно превышать 2000 символов'
    
    # Если оригинальное название пустое, но русское задано, используем русское
    if (not film.get('title') or film['title'].strip() == '') and film.get('title_ru'):
        film['title'] = film['title_ru']
    
    return errors, film

@lab7.route('/lab7/')
def main():
    return render_template('lab7/index.html')

@lab7.route('/lab7/rest-api/films/', methods=['GET'])
def get_films():
    conn, cur = db_connect()
    
    try:
        if current_app.config.get('DB_TYPE') == 'postgres':
            cur.execute('SELECT * FROM films ORDER BY id')
        else:
            cur.execute('SELECT * FROM films ORDER BY id')
        
        films_rows = cur.fetchall()
        
        # Конвертируем результаты в список словарей
        films = []
        for film_row in films_rows:
            film = convert_to_dict(film_row)
            # Преобразуем типы данных для совместимости
            film['id'] = int(film['id'])
            film['year'] = int(film['year'])
            films.append(film)
        
        db_close(conn, cur)
        return jsonify(films)
    except Exception as e:
        print(f"Ошибка при получении фильмов из БД: {str(e)}")
        db_close(conn, cur)
        return jsonify([])

@lab7.route('/lab7/rest-api/films/<int:id>', methods=['GET'])
def get_film(id):
    conn, cur = db_connect()
    
    try:
        if current_app.config.get('DB_TYPE') == 'postgres':
            cur.execute('SELECT * FROM films WHERE id = %s', (id,))
        else:
            cur.execute('SELECT * FROM films WHERE id = ?', (id,))
        
        film_row = cur.fetchone()
        db_close(conn, cur)
        
        if not film_row:
            return jsonify({"error": "Film not found"}), 404
        
        film = convert_to_dict(film_row)
        film['id'] = int(film['id'])
        film['year'] = int(film['year'])
        
        return jsonify(film)
    except Exception as e:
        print(f"Ошибка при получении фильма из БД: {str(e)}")
        db_close(conn, cur)
        return jsonify({"error": "Database error"}), 500

@lab7.route('/lab7/rest-api/films/<int:id>', methods=['DELETE'])
def del_film(id):
    conn, cur = db_connect()
    
    try:
        # Проверяем существование фильма
        if current_app.config.get('DB_TYPE') == 'postgres':
            cur.execute('SELECT * FROM films WHERE id = %s', (id,))
        else:
            cur.execute('SELECT * FROM films WHERE id = ?', (id,))
        
        film_row = cur.fetchone()
        
        if not film_row:
            db_close(conn, cur)
            return jsonify({"error": "Film not found"}), 404
        
        # Удаляем фильм
        if current_app.config.get('DB_TYPE') == 'postgres':
            cur.execute('DELETE FROM films WHERE id = %s', (id,))
        else:
            cur.execute('DELETE FROM films WHERE id = ?', (id,))
        
        db_close(conn, cur)
        return '', 204
    except Exception as e:
        print(f"Ошибка при удалении фильма из БД: {str(e)}")
        db_close(conn, cur)
        return jsonify({"error": "Database error"}), 500

@lab7.route('/lab7/rest-api/films/<int:id>', methods=['PUT'])
def put_film(id):
    conn, cur = db_connect()
    
    try:
        # Проверяем существование фильма
        if current_app.config.get('DB_TYPE') == 'postgres':
            cur.execute('SELECT * FROM films WHERE id = %s', (id,))
        else:
            cur.execute('SELECT * FROM films WHERE id = ?', (id,))
        
        film_row = cur.fetchone()
        
        if not film_row:
            db_close(conn, cur)
            return jsonify({"error": "Film not found"}), 404
        
        film_data = request.get_json()
        
        # Валидация данных
        errors, validated_film = validate_film_data(film_data)
        if errors:
            db_close(conn, cur)
            return jsonify(errors), 400
        
        # Обновляем фильм в БД
        if current_app.config.get('DB_TYPE') == 'postgres':
            cur.execute('''
                UPDATE films 
                SET title = %s, title_ru = %s, year = %s, description = %s 
                WHERE id = %s
            ''', (validated_film['title'], validated_film['title_ru'], 
                  validated_film['year'], validated_film['description'], id))
        else:
            cur.execute('''
                UPDATE films 
                SET title = ?, title_ru = ?, year = ?, description = ? 
                WHERE id = ?
            ''', (validated_film['title'], validated_film['title_ru'], 
                  validated_film['year'], validated_film['description'], id))
        
        # Получаем обновленный фильм
        if current_app.config.get('DB_TYPE') == 'postgres':
            cur.execute('SELECT * FROM films WHERE id = %s', (id,))
        else:
            cur.execute('SELECT * FROM films WHERE id = ?', (id,))
        
        updated_film_row = cur.fetchone()
        updated_film = convert_to_dict(updated_film_row)
        updated_film['id'] = int(updated_film['id'])
        updated_film['year'] = int(updated_film['year'])
        
        db_close(conn, cur)
        return jsonify(updated_film), 200
    except Exception as e:
        print(f"Ошибка при обновлении фильма в БД: {str(e)}")
        db_close(conn, cur)
        return jsonify({"error": "Database error"}), 500

@lab7.route('/lab7/rest-api/films/', methods=['POST'])
def add_film():
    conn, cur = db_connect()
    
    try:
        film_data = request.get_json()
        
        # Валидация данных
        errors, validated_film = validate_film_data(film_data)
        if errors:
            db_close(conn, cur)
            return jsonify(errors), 400
        
        # Добавляем новый фильм в БД
        if current_app.config.get('DB_TYPE') == 'postgres':
            cur.execute('''
                INSERT INTO films (title, title_ru, year, description)
                VALUES (%s, %s, %s, %s)
                RETURNING id
            ''', (validated_film['title'], validated_film['title_ru'], 
                  validated_film['year'], validated_film['description']))
            
            new_id = cur.fetchone()['id']
        else:
            cur.execute('''
                INSERT INTO films (title, title_ru, year, description)
                VALUES (?, ?, ?, ?)
            ''', (validated_film['title'], validated_film['title_ru'], 
                  validated_film['year'], validated_film['description']))
            
            new_id = cur.lastrowid
        
        db_close(conn, cur)
        return jsonify({"id": new_id}), 201
    except Exception as e:
        print(f"Ошибка при добавлении фильма в БД: {str(e)}")
        db_close(conn, cur)
        return jsonify({"error": "Database error"}), 500