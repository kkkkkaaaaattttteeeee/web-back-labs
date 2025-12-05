from flask import Blueprint, render_template, request, session, current_app
import psycopg2
from psycopg2.extras import RealDictCursor
import sqlite3
from os import path

lab6 = Blueprint('lab6', __name__)

# Функции для работы с БД (аналогичные тем, что в lab5.py)
def db_connect():
    """Универсальная функция для подключения к БД"""
    if current_app.config['DB_TYPE'] == 'postgres':
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

# УДАЛЯЕМ переменную offices - больше она не нужна!
# offices = [] 
# for i in range(1, 11):
#     offices.append({"number": i, "tenant": "", "price": 900 + i % 3})

@lab6.route("/lab6/")
def main():
    return render_template('lab6/lab6.html')

@lab6.route('/lab6/json-rpc-api/', methods=['POST'])
def api():
    data = request.json
    id = data['id']
    
    if data['method'] == 'info':
        # Получаем данные из базы данных
        try:
            conn, cur = db_connect()
            
            # Выполняем запрос в зависимости от типа БД
            if current_app.config['DB_TYPE'] == 'postgres':
                cur.execute("SELECT * FROM offices ORDER BY number;")
            else:
                cur.execute("SELECT * FROM offices ORDER BY number;")
            
            offices_rows = cur.fetchall()
            
            # Конвертируем результаты в список словарей
            offices = []
            for office_row in offices_rows:
                office = convert_to_dict(office_row)
                # Преобразуем типы данных для совместимости
                office['number'] = int(office['number'])
                office['price'] = int(office['price'])
                if office['tenant'] is None:
                    office['tenant'] = ""
                offices.append(office)
            
            db_close(conn, cur)
            
            return {
                'jsonrpc': '2.0',
                'result': offices,
                'id': id
            }
        except Exception as e:
            print(f"Ошибка при получении офисов из БД: {str(e)}")
            # В случае ошибки возвращаем пустой список
            return {
                'jsonrpc': '2.0',
                'result': [],
                'id': id
            }

    login = session.get('user_login')
    if not login:
        return {
            'jsonrpc': '2.0',
            'error': {
                'code': 1,
                'message': 'Unauthorized'
            },
            'id': id
        }
    
    if data['method'] == 'booking':
        office_number = data['params']
        
        try:
            conn, cur = db_connect()
            
            # Проверяем, существует ли офис и забронирован ли он
            if current_app.config['DB_TYPE'] == 'postgres':
                cur.execute("SELECT * FROM offices WHERE number = %s;", (office_number,))
            else:
                cur.execute("SELECT * FROM offices WHERE number = ?;", (office_number,))
            
            office_row = cur.fetchone()
            
            if not office_row:
                db_close(conn, cur)
                return {
                    'jsonrpc': '2.0',
                    'error': {
                        'code': 6,
                        'message': 'Office not found'
                    },
                    'id': id
                }
            
            office = convert_to_dict(office_row)
            
            # Проверяем, не забронирован ли уже офис
            if office['tenant'] and office['tenant'].strip():  # Проверяем, что tenant не пустой
                db_close(conn, cur)
                return {
                    'jsonrpc': '2.0',
                    'error': {
                        'code': 2,
                        'message': 'Already booked'
                    },
                    'id': id
                }
            
            # Бронируем офис
            if current_app.config['DB_TYPE'] == 'postgres':
                cur.execute("UPDATE offices SET tenant = %s WHERE number = %s;", (login, office_number))
            else:
                cur.execute("UPDATE offices SET tenant = ? WHERE number = ?;", (login, office_number))
            
            db_close(conn, cur)
            
            return {
                'jsonrpc': '2.0',
                'result': 'success',
                'id': id
            }
            
        except Exception as e:
            print(f"Ошибка при бронировании офиса: {str(e)}")
            return {
                'jsonrpc': '2.0',
                'error': {
                    'code': 5,
                    'message': f'Database error: {str(e)}'
                },
                'id': id
            }
    
    if data['method'] == 'cancellation':
        office_number = data['params']
        
        try:
            conn, cur = db_connect()
            
            # Получаем информацию об офисе
            if current_app.config['DB_TYPE'] == 'postgres':
                cur.execute("SELECT * FROM offices WHERE number = %s;", (office_number,))
            else:
                cur.execute("SELECT * FROM offices WHERE number = ?;", (office_number,))
            
            office_row = cur.fetchone()
            
            if not office_row:
                db_close(conn, cur)
                return {
                    'jsonrpc': '2.0',
                    'error': {
                        'code': 6,
                        'message': 'Office not found'
                    },
                    'id': id
                }
            
            office = convert_to_dict(office_row)
            
            # Проверяем, забронирован ли офис
            if not office['tenant'] or office['tenant'].strip() == "":
                db_close(conn, cur)
                return {
                    'jsonrpc': '2.0',
                    'error': {
                        'code': 3,
                        'message': 'Office is not booked'
                    },
                    'id': id
                }
            
            # Проверяем, принадлежит ли бронь текущему пользователю
            if office['tenant'] != login:
                db_close(conn, cur)
                return {
                    'jsonrpc': '2.0',
                    'error': {
                        'code': 4,
                        'message': 'Cannot cancel other user\'s booking'
                    },
                    'id': id
                }
            
            # Освобождаем офис
            if current_app.config['DB_TYPE'] == 'postgres':
                cur.execute("UPDATE offices SET tenant = %s WHERE number = %s;", ('', office_number))
            else:
                cur.execute("UPDATE offices SET tenant = ? WHERE number = ?;", ('', office_number))
            
            db_close(conn, cur)
            
            return {
                'jsonrpc': '2.0',
                'result': 'success',
                'id': id
            }
            
        except Exception as e:
            print(f"Ошибка при отмене брони: {str(e)}")
            return {
                'jsonrpc': '2.0',
                'error': {
                    'code': 5,
                    'message': f'Database error: {str(e)}'
                },
                'id': id
            }
    
    return {
        'jsonrpc': '2.0',
        'error': {
            'code': -32601,
            'message': 'Method not found'
        },
        'id': id
    }