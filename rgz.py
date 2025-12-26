from flask import Blueprint, request, render_template, redirect, session, current_app, flash, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
import os
import sqlite3
import datetime
import random
import json
from decimal import Decimal
from functools import wraps
import pathlib

rgz = Blueprint('rgz', __name__, template_folder='templates/rgz', url_prefix='/rgz', static_folder='static/rgz')

class CustomJSONEncoder(json.JSONEncoder):
    """Кастомный JSON энкодер для обработки Decimal и datetime"""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.date):
            return obj.strftime('%Y-%m-%d')
        return super(CustomJSONEncoder, self).default(obj)

def get_db_path():
    """Определяет путь к базе данных в зависимости от среды"""
    if 'PYTHONANYWHERE_DOMAIN' in os.environ:
        # На PythonAnywhere
        return '/home/obedinaekaterina/web-back-labs/rgz_database.db'
    else:
        # Локально
        base_dir = pathlib.Path(__file__).parent.parent
        return base_dir / 'rgz_database.db'

def db_connect():
    """Универсальное подключение к базе данных"""
    try:
        db_type = current_app.config.get('DB_TYPE', 'postgres')
        
        if db_type == 'postgres':
            # PostgreSQL подключение
            import psycopg2
            from psycopg2.extras import RealDictCursor
            
            conn = psycopg2.connect(
                host='127.0.0.1',
                database='bank_db',
                user='obedina_ekaterina_knowledge_base',
                password='123',
                client_encoding='UTF8'
            )
            cur = conn.cursor(cursor_factory=RealDictCursor)
            return conn, cur
        else:
            # SQLite подключение
            db_path = get_db_path()
            conn = sqlite3.connect(str(db_path))
            
            # Включаем поддержку внешних ключей
            conn.execute("PRAGMA foreign_keys = ON")
            
            # Настраиваем возврат строк в виде словаря
            def dict_factory(cursor, row):
                d = {}
                for idx, col in enumerate(cursor.description):
                    d[col[0]] = row[idx]
                return d
            conn.row_factory = dict_factory
            
            cur = conn.cursor()
            return conn, cur
            
    except Exception as e:
        print(f"Database connection error: {e}")
        raise

def db_close(conn, cur):
    """Универсальное закрытие соединения с базой данных"""
    try:
        if conn:
            conn.commit()
        if cur:
            cur.close()
        if conn:
            conn.close()
    except Exception as e:
        print(f"Database close error: {e}")

def execute_query(cur, sql, params=None):
    """Универсальное выполнение SQL-запросов для разных СУБД"""
    if params is None:
        params = ()
    
    db_type = current_app.config.get('DB_TYPE', 'postgres')
    
    try:
        # Для SQLite преобразуем boolean значения
        if db_type == 'sqlite':
            params = list(params)
            for i, param in enumerate(params):
                if isinstance(param, bool):
                    params[i] = 1 if param else 0
        
        cur.execute(sql, params)
        return cur
    except Exception as e:
        print(f"Query execution error: {e}")
        raise

def safe_convert_value(value):
    """Безопасное преобразование значения для JSON"""
    if value is None:
        return None
    elif isinstance(value, Decimal):
        return float(value)
    elif isinstance(value, datetime.datetime):
        return value.strftime('%Y-%m-%d %H:%M:%S')
    elif isinstance(value, datetime.date):
        return value.strftime('%Y-%m-%d')
    elif isinstance(value, bytes):
        try:
            return value.decode('utf-8')
        except UnicodeDecodeError:
            return value.decode('latin-1', errors='ignore')
        except:
            return str(value)
    elif isinstance(value, (int, float, str, bool)):
        return value
    else:
        return str(value)

def convert_to_dict(row):
    """Конвертирует строку из БД в словарь с безопасными значениями"""
    if row is None:
        return None
    
    result = {}
    if hasattr(row, 'keys'):  # Для словарей и RealDictCursor
        for key in row.keys():
            result[key] = safe_convert_value(row[key])
    elif isinstance(row, (tuple, list)):  # Для обычных кортежей
        # Этот случай маловероятен, но на всякий случай
        for i, value in enumerate(row):
            result[f'col_{i}'] = safe_convert_value(value)
    
    return result

def login_required(f):
    """Декоратор для проверки авторизации"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect('/rgz/login')
        return f(*args, **kwargs)
    return decorated_function

def manager_required(f):
    """Декоратор для проверки прав менеджера"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_role' not in session or session['user_role'] != 'manager':
            flash('Доступ только для менеджеров банка', 'error')
            return redirect('/rgz/')
        return f(*args, **kwargs)
    return decorated_function

def client_required(f):
    """Декоратор для проверки прав клиента"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_role' not in session or session['user_role'] != 'client':
            flash('Доступ только для клиентов банка', 'error')
            return redirect('/rgz/')
        return f(*args, **kwargs)
    return decorated_function

def get_param_style():
    """Возвращает стиль параметров для текущей СУБД"""
    db_type = current_app.config.get('DB_TYPE', 'postgres')
    return '%s' if db_type == 'postgres' else '?'

def init_sqlite_db():
    """Инициализация базы данных SQLite"""
    try:
        db_path = get_db_path()
        
        # Проверяем, существует ли директория
        os.makedirs(os.path.dirname(str(db_path)), exist_ok=True)
        
        conn = sqlite3.connect(str(db_path))
        cur = conn.cursor()
        
        # Создаем таблицы, если их нет
        cur.execute('''
            CREATE TABLE IF NOT EXISTS rgz_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                login VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(200) NOT NULL,
                full_name VARCHAR(100) NOT NULL,
                phone VARCHAR(20),
                account_number VARCHAR(20) UNIQUE,
                balance DECIMAL(15,2) DEFAULT 0.00,
                role VARCHAR(10) NOT NULL CHECK (role IN ('client', 'manager')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cur.execute('''
            CREATE TABLE IF NOT EXISTS rgz_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_account VARCHAR(20),
                to_account VARCHAR(20) NOT NULL,
                amount DECIMAL(15,2) NOT NULL,
                transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                description VARCHAR(200)
            )
        ''')
        
        # Создаем индексы
        cur.execute('CREATE INDEX IF NOT EXISTS idx_rgz_transactions_from_account ON rgz_transactions(from_account)')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_rgz_transactions_to_account ON rgz_transactions(to_account)')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_rgz_users_account_number ON rgz_users(account_number)')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_rgz_users_phone ON rgz_users(phone)')
        
        # Проверяем, есть ли администратор
        cur.execute("SELECT COUNT(*) FROM rgz_users WHERE role = 'manager'")
        if cur.fetchone()[0] == 0:
            # Создаем администратора по умолчанию
            admin_password = generate_password_hash('admin123', method='scrypt')
            cur.execute('''
                INSERT INTO rgz_users (login, password, full_name, role) 
                VALUES (?, ?, ?, ?)
            ''', ('admin', admin_password, 'Администратор', 'manager'))
        
        conn.commit()
        conn.close()
        print(f"База данных SQLite инициализирована: {db_path}")
        return True
    except Exception as e:
        print(f"Ошибка инициализации SQLite базы данных: {e}")
        return False

@rgz.route('/api/login', methods=['POST'])
def api_simple_login():
    """Упрощенная авторизация для отладки"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Отсутствуют данные JSON'}), 400
    
    login = data.get('login')
    password = data.get('password')
    
    if not login or not password:
        return jsonify({'error': 'Логин и пароль обязательны'}), 400
    
    conn = None
    cur = None
    try:
        conn, cur = db_connect()
        
        param_style = get_param_style()
        query = f"SELECT * FROM rgz_users WHERE login = {param_style}"
        execute_query(cur, query, (login,))
        user_row = cur.fetchone()
        
        if not user_row:
            db_close(conn, cur)
            return jsonify({'error': 'Пользователь не найден'}), 401
        
        user = convert_to_dict(user_row)
        stored_password = user.get('password', '')
        
        # Проверяем пароль в зависимости от его формата
        password_correct = False
        
        # Если пароль хранится как хеш
        if stored_password and (stored_password.startswith('scrypt:') or stored_password.startswith('pbkdf2:')):
            try:
                password_correct = check_password_hash(stored_password, password)
            except Exception as hash_error:
                print(f"Hash check error: {hash_error}")
                password_correct = False
        else:
            # Если пароль хранится в открытом виде (временная мера)
            password_correct = (stored_password == password)
        
        if password_correct:
            # Успешный вход
            session['user_id'] = user['id']
            session['user_login'] = user['login']
            session['user_role'] = user['role']
            session['user_full_name'] = user['full_name']
            
            if user['role'] == 'client':
                session['user_account'] = user.get('account_number', '')
                session['user_balance'] = float(user.get('balance', 0.0))
            
            # Удаляем пароль из ответа
            if 'password' in user:
                del user['password']
            
            db_close(conn, cur)
            return jsonify({
                'success': True,
                'user': user
            })
        else:
            db_close(conn, cur)
            return jsonify({'error': 'Неверный пароль'}), 401
            
    except Exception as e:
        print(f"Login error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Внутренняя ошибка сервера'}), 500
    finally:
        if conn or cur:
            try:
                db_close(conn, cur)
            except:
                pass

@rgz.route('/api/logout', methods=['POST'])
def api_logout():
    """API для выхода"""
    session.clear()
    return jsonify({'success': True})

@rgz.route('/api/transfer', methods=['POST'])
@login_required
@client_required
def api_transfer():
    """API для перевода денег (только для клиентов)"""
    data = request.get_json()
    to_account = data.get('to_account')
    amount = float(data.get('amount', 0))
    description = data.get('description', '')
    
    if amount <= 0:
        return jsonify({'error': 'Сумма должна быть положительной'}), 400
    
    conn = None
    cur = None
    try:
        conn, cur = db_connect()
        param_style = get_param_style()
        
        # Получаем данные отправителя
        query = f"SELECT * FROM rgz_users WHERE id = {param_style}"
        execute_query(cur, query, (session['user_id'],))
        sender = convert_to_dict(cur.fetchone())
        
        if not sender:
            db_close(conn, cur)
            return jsonify({'error': 'Отправитель не найден'}), 404
        
        if float(sender.get('balance', 0)) < amount:
            db_close(conn, cur)
            return jsonify({'error': 'Недостаточно средств'}), 400
        
        # Ищем получателя по номеру счета или телефону
        query = f"""
            SELECT * FROM rgz_users 
            WHERE (account_number = {param_style} OR phone = {param_style}) 
            AND role = 'client'
        """
        execute_query(cur, query, (to_account, to_account))
        receiver = cur.fetchone()
        
        if not receiver:
            db_close(conn, cur)
            return jsonify({'error': 'Получатель не найден'}), 404
        
        receiver = convert_to_dict(receiver)
        
        if receiver['id'] == sender['id']:
            db_close(conn, cur)
            return jsonify({'error': 'Нельзя перевести себе'}), 400
        
        # Выполняем перевод
        query = f"UPDATE rgz_users SET balance = balance - {param_style} WHERE id = {param_style}"
        execute_query(cur, query, (amount, sender['id']))
        
        query = f"UPDATE rgz_users SET balance = balance + {param_style} WHERE id = {param_style}"
        execute_query(cur, query, (amount, receiver['id']))
        
        # Записываем транзакцию
        db_type = current_app.config.get('DB_TYPE', 'postgres')
        if db_type == 'postgres':
            query = """
                INSERT INTO rgz_transactions 
                (from_account, to_account, amount, description) 
                VALUES (%s, %s, %s, %s)
                RETURNING id
            """
        else:
            query = """
                INSERT INTO rgz_transactions 
                (from_account, to_account, amount, description) 
                VALUES (?, ?, ?, ?)
            """
        
        execute_query(cur, query, (sender.get('account_number'), receiver['account_number'], amount, description))
        
        # Получаем ID транзакции
        if db_type == 'postgres':
            transaction_id = cur.fetchone()['id']
        else:
            transaction_id = cur.lastrowid
        
        # Получаем обновленный баланс отправителя
        query = f"SELECT balance FROM rgz_users WHERE id = {param_style}"
        execute_query(cur, query, (sender['id'],))
        new_balance = cur.fetchone()['balance']
        
        # Обновляем баланс в сессии
        if session.get('user_role') == 'client' and session.get('user_id') == sender['id']:
            session['user_balance'] = float(new_balance)
        
        db_close(conn, cur)
        
        return json.dumps({
            'success': True,
            'message': f'Перевод на сумму {amount} руб. выполнен успешно',
            'transaction_id': transaction_id,
            'new_balance': float(new_balance),
            'details': {
                'from_account': sender.get('account_number'),
                'to_account': receiver['account_number'],
                'to_name': receiver['full_name'],
                'amount': amount,
                'description': description
            }
        }, cls=CustomJSONEncoder, ensure_ascii=False)
        
    except Exception as e:
        print(f"Transfer error: {e}")
        if conn or cur:
            db_close(conn, cur)
        return jsonify({'error': str(e)}), 500

@rgz.route('/api/transactions')
@login_required
def api_transactions():
    """API для получения истории транзакций"""
    conn = None
    cur = None
    try:
        conn, cur = db_connect()
        param_style = get_param_style()
        
        if session.get('user_role') == 'client':
            user_account = session.get('user_account')
            query = f"""
                SELECT t.*, 
                       u1.full_name as from_name,
                       u2.full_name as to_name
                FROM rgz_transactions t
                LEFT JOIN rgz_users u1 ON t.from_account = u1.account_number
                LEFT JOIN rgz_users u2 ON t.to_account = u2.account_number
                WHERE t.from_account = {param_style} OR t.to_account = {param_style} 
                ORDER BY t.transaction_date DESC
            """
            execute_query(cur, query, (user_account, user_account))
        else:
            query = """
                SELECT t.*, 
                       u1.full_name as from_name,
                       u2.full_name as to_name
                FROM rgz_transactions t
                LEFT JOIN rgz_users u1 ON t.from_account = u1.account_number
                LEFT JOIN rgz_users u2 ON t.to_account = u2.account_number
                ORDER BY t.transaction_date DESC
            """
            execute_query(cur, query)
        
        transactions = []
        for row in cur.fetchall():
            transaction = convert_to_dict(row)
            # Добавляем отформатированную дату для удобства
            if transaction.get('transaction_date'):
                try:
                    if isinstance(transaction['transaction_date'], str):
                        for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S.%f', '%Y-%m-%d %H:%M:%S.%f']:
                            try:
                                dt = datetime.datetime.strptime(transaction['transaction_date'], fmt)
                                transaction['formatted_date'] = dt.strftime('%d.%m.%Y %H:%M')
                                break
                            except:
                                continue
                    else:
                        transaction['formatted_date'] = transaction['transaction_date'].strftime('%d.%m.%Y %H:%M')
                except:
                    transaction['formatted_date'] = str(transaction.get('transaction_date', ''))
            transactions.append(transaction)
        
        db_close(conn, cur)
        return json.dumps({'transactions': transactions}, cls=CustomJSONEncoder, ensure_ascii=False)
        
    except Exception as e:
        print(f"Transactions error: {e}")
        if conn or cur:
            db_close(conn, cur)
        return jsonify({'error': str(e)}), 500

@rgz.route('/api/users')
@login_required
@manager_required
def api_users():
    """API для получения списка пользователей (только для менеджеров)"""
    conn = None
    cur = None
    try:
        conn, cur = db_connect()
        
        # Для SQLite нужно использовать COALESCE немного иначе
        db_type = current_app.config.get('DB_TYPE', 'postgres')
        if db_type == 'postgres':
            query = """
                SELECT id, login, full_name, phone, account_number, 
                       COALESCE(balance, 0) as balance, role, 
                       DATE(created_at) as created_date
                FROM rgz_users 
                ORDER BY role, full_name
            """
        else:
            query = """
                SELECT id, login, full_name, phone, account_number, 
                       IFNULL(balance, 0) as balance, role, 
                       DATE(created_at) as created_date
                FROM rgz_users 
                ORDER BY role, full_name
            """
        
        execute_query(cur, query)
        
        users = []
        for row in cur.fetchall():
            user = convert_to_dict(row)
            if user.get('balance') is not None:
                try:
                    user['balance'] = float(user['balance'])
                except:
                    user['balance'] = 0.0
            else:
                user['balance'] = 0.0
            users.append(user)
        
        db_close(conn, cur)
        return json.dumps({'users': users}, cls=CustomJSONEncoder, ensure_ascii=False)
        
    except Exception as e:
        print(f"Users error: {e}")
        if conn or cur:
            db_close(conn, cur)
        return jsonify({'error': str(e)}), 500

@rgz.route('/api/user', methods=['POST'])
@login_required
@manager_required
def api_create_user():
    """API для создания пользователя с хешированием пароля"""
    data = request.get_json()
    
    required_fields = ['login', 'password', 'full_name', 'role']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'Поле {field} обязательно'}), 400
    
    conn = None
    cur = None
    try:
        conn, cur = db_connect()
        param_style = get_param_style()
        
        # Проверяем уникальность логина
        query = f"SELECT id FROM rgz_users WHERE login = {param_style}"
        execute_query(cur, query, (data['login'],))
        if cur.fetchone():
            db_close(conn, cur)
            return jsonify({'error': 'Пользователь с таким логином уже существует'}), 400
        
        # Всегда хешируем пароль при создании
        hashed_password = generate_password_hash(data['password'], method='scrypt')
        
        db_type = current_app.config.get('DB_TYPE', 'postgres')
        
        if data['role'] == 'client':
            phone = data.get('phone', '')
            if not phone:
                db_close(conn, cur)
                return jsonify({'error': 'Для клиента обязателен телефон'}), 400
            
            # Генерируем уникальный номер счета
            account_number = f'40817810{random.randint(1000000000, 9999999999)}'
            
            # Проверяем уникальность номера счета
            query = f"SELECT id FROM rgz_users WHERE account_number = {param_style}"
            execute_query(cur, query, (account_number,))
            if cur.fetchone():
                account_number = f'40817810{random.randint(1000000000, 9999999999)}'
            
            balance = float(data.get('balance', 10000.00))
            
            if db_type == 'postgres':
                query = """
                    INSERT INTO rgz_users 
                    (login, password, full_name, phone, account_number, balance, role) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """
            else:
                query = """
                    INSERT INTO rgz_users 
                    (login, password, full_name, phone, account_number, balance, role) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """
            
            execute_query(cur, query, (
                data['login'],
                hashed_password,
                data['full_name'],
                phone,
                account_number,
                balance,
                'client'
            ))
        else:
            # Для менеджера
            if db_type == 'postgres':
                query = """
                    INSERT INTO rgz_users 
                    (login, password, full_name, role) 
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                """
            else:
                query = """
                    INSERT INTO rgz_users 
                    (login, password, full_name, role) 
                    VALUES (?, ?, ?, ?)
                """
            
            execute_query(cur, query, (
                data['login'],
                hashed_password,
                data['full_name'],
                'manager'
            ))
        
        if db_type == 'postgres':
            new_user_id = cur.fetchone()['id']
        else:
            new_user_id = cur.lastrowid
        
        db_close(conn, cur)
        return jsonify({
            'success': True, 
            'message': 'Пользователь создан',
            'user_id': new_user_id
        })
        
    except Exception as e:
        print(f"Create user error: {e}")
        if conn or cur:
            db_close(conn, cur)
        return jsonify({'error': str(e)}), 500

@rgz.route('/api/user/<int:user_id>', methods=['PUT'])
@login_required
@manager_required
def api_update_user(user_id):
    """API для обновления пользователя (только для менеджеров)"""
    if user_id == session.get('user_id'):
        return jsonify({'error': 'Нельзя редактировать свой аккаунт'}), 400
    
    data = request.get_json()
    
    conn = None
    cur = None
    try:
        conn, cur = db_connect()
        param_style = get_param_style()
        
        # Получаем текущие данные пользователя
        query = f"SELECT * FROM rgz_users WHERE id = {param_style}"
        execute_query(cur, query, (user_id,))
        user_row = cur.fetchone()
        
        if not user_row:
            db_close(conn, cur)
            return jsonify({'error': 'Пользователь не найден'}), 404
        
        user = convert_to_dict(user_row)
        
        # Обновляем поля в зависимости от роли
        if user['role'] == 'client':
            full_name = data.get('full_name', user['full_name'])
            phone = data.get('phone', user.get('phone', ''))
            balance = float(data.get('balance', user['balance']))
            
            query = f"""
                UPDATE rgz_users 
                SET full_name = {param_style}, phone = {param_style}, balance = {param_style} 
                WHERE id = {param_style}
            """
            execute_query(cur, query, (full_name, phone, balance, user_id))
        else:
            full_name = data.get('full_name', user['full_name'])
            query = f"UPDATE rgz_users SET full_name = {param_style} WHERE id = {param_style}"
            execute_query(cur, query, (full_name, user_id))
        
        # Если нужно обновить пароль
        if data.get('new_password'):
            hashed_password = generate_password_hash(data['new_password'], method='scrypt')
            query = f"UPDATE rgz_users SET password = {param_style} WHERE id = {param_style}"
            execute_query(cur, query, (hashed_password, user_id))
        
        db_close(conn, cur)
        return jsonify({'success': True, 'message': 'Пользователь обновлен'})
        
    except Exception as e:
        print(f"Update user error: {e}")
        if conn or cur:
            db_close(conn, cur)
        return jsonify({'error': str(e)}), 500

@rgz.route('/api/user/<int:user_id>', methods=['DELETE'])
@login_required
@manager_required
def api_delete_user(user_id):
    """API для удаления пользователя (только для менеджеров)"""
    if user_id == session.get('user_id'):
        return jsonify({'error': 'Нельзя удалить свой аккаунт'}), 400
    
    conn = None
    cur = None
    try:
        conn, cur = db_connect()
        param_style = get_param_style()
        
        # Проверяем, что пользователь существует
        query = f"SELECT * FROM rgz_users WHERE id = {param_style}"
        execute_query(cur, query, (user_id,))
        user_row = cur.fetchone()
        
        if not user_row:
            db_close(conn, cur)
            return jsonify({'error': 'Пользователь не найден'}), 404
        
        user = convert_to_dict(user_row)
        
        # Удаляем связанные транзакции пользователя (если он клиент)
        if user.get('role') == 'client' and user.get('account_number'):
            query = f"DELETE FROM rgz_transactions WHERE from_account = {param_style} OR to_account = {param_style}"
            execute_query(cur, query, (user['account_number'], user['account_number']))
        
        # Удаляем пользователя
        query = f"DELETE FROM rgz_users WHERE id = {param_style}"
        execute_query(cur, query, (user_id,))
        
        db_close(conn, cur)
        return jsonify({'success': True, 'message': 'Пользователь удален'})
        
    except Exception as e:
        print(f"Delete user error: {e}")
        if conn or cur:
            db_close(conn, cur)
        return jsonify({'error': str(e)}), 500

@rgz.route('/api/user/current')
@login_required
def api_current_user():
    """API для получения данных текущего пользователя"""
    conn = None
    cur = None
    try:
        conn, cur = db_connect()
        param_style = get_param_style()
        query = f"SELECT * FROM rgz_users WHERE id = {param_style}"
        execute_query(cur, query, (session['user_id'],))
        user_row = cur.fetchone()
        
        if not user_row:
            db_close(conn, cur)
            return jsonify({'error': 'Пользователь не найден'}), 404
        
        user = convert_to_dict(user_row)
        
        # Убираем пароль
        if 'password' in user:
            del user['password']
        
        db_close(conn, cur)
        return json.dumps({'user': user}, cls=CustomJSONEncoder, ensure_ascii=False)
        
    except Exception as e:
        print(f"Current user error: {e}")
        if conn or cur:
            db_close(conn, cur)
        return jsonify({'error': str(e)}), 500

@rgz.route('/api/statistics')
@login_required
@manager_required
def api_statistics():
    """API для получения статистики (только для менеджеров)"""
    conn = None
    cur = None
    try:
        conn, cur = db_connect()
        db_type = current_app.config.get('DB_TYPE', 'postgres')
        
        # Основная статистика
        query = "SELECT COUNT(*) as total_users FROM rgz_users"
        execute_query(cur, query)
        total_users = cur.fetchone()['total_users']
        
        query = "SELECT COUNT(*) as total_clients FROM rgz_users WHERE role = 'client'"
        execute_query(cur, query)
        total_clients = cur.fetchone()['total_clients']
        
        query = "SELECT COUNT(*) as total_managers FROM rgz_users WHERE role = 'manager'"
        execute_query(cur, query)
        total_managers = cur.fetchone()['total_managers']
        
        query = "SELECT COALESCE(SUM(balance), 0) as total_balance FROM rgz_users WHERE role = 'client'"
        execute_query(cur, query)
        total_balance_result = cur.fetchone()['total_balance']
        total_balance = float(total_balance_result) if total_balance_result else 0.0
        
        query = "SELECT COUNT(*) as total_transactions FROM rgz_transactions"
        execute_query(cur, query)
        total_transactions = cur.fetchone()['total_transactions']
        
        # Статистика по активным пользователям
        if db_type == 'postgres':
            query = """
                SELECT COUNT(DISTINCT u.id) as active_clients
                FROM rgz_users u
                WHERE u.role = 'client' AND EXISTS (
                    SELECT 1 FROM rgz_transactions t 
                    WHERE t.from_account = u.account_number OR t.to_account = u.account_number
                )
            """
        else:
            query = """
                SELECT COUNT(DISTINCT u.id) as active_clients
                FROM rgz_users u
                WHERE u.role = 'client' AND (
                    EXISTS (SELECT 1 FROM rgz_transactions t WHERE t.from_account = u.account_number)
                    OR EXISTS (SELECT 1 FROM rgz_transactions t WHERE t.to_account = u.account_number)
                )
            """
        execute_query(cur, query)
        active_clients = cur.fetchone()['active_clients']
        
        # Статистика по транзакциям за последние 7 дней
        if db_type == 'postgres':
            query = """
                SELECT 
                    DATE(transaction_date) as date,
                    COUNT(*) as transactions_count,
                    SUM(amount) as total_amount
                FROM rgz_transactions 
                WHERE transaction_date >= CURRENT_DATE - INTERVAL '7 days'
                GROUP BY DATE(transaction_date)
                ORDER BY date
            """
        else:
            query = """
                SELECT 
                    DATE(transaction_date) as date,
                    COUNT(*) as transactions_count,
                    SUM(amount) as total_amount
                FROM rgz_transactions 
                WHERE transaction_date >= date('now', '-7 days')
                GROUP BY DATE(transaction_date)
                ORDER BY date
            """
        
        execute_query(cur, query)
        weekly_stats = []
        for row in cur.fetchall():
            stats = convert_to_dict(row)
            weekly_stats.append(stats)
        
        # Топ 5 клиентов по балансу
        query = """
            SELECT full_name, balance 
            FROM rgz_users 
            WHERE role = 'client' 
            ORDER BY balance DESC 
            LIMIT 5
        """
        execute_query(cur, query)
        
        top_clients = []
        for row in cur.fetchall():
            client = convert_to_dict(row)
            if client.get('balance'):
                client['balance'] = float(client['balance'])
            top_clients.append(client)
        
        db_close(conn, cur)
        
        return json.dumps({
            'statistics': {
                'total_users': total_users,
                'total_clients': total_clients,
                'total_managers': total_managers,
                'total_balance': total_balance,
                'total_transactions': total_transactions,
                'active_clients': active_clients,
                'inactive_clients': total_clients - active_clients,
                'weekly_stats': weekly_stats,
                'top_clients': top_clients
            }
        }, cls=CustomJSONEncoder, ensure_ascii=False)
        
    except Exception as e:
        print(f"Statistics error: {e}")
        if conn or cur:
            db_close(conn, cur)
        return jsonify({'error': str(e)}), 500

# HTML Routes
@rgz.route('/')
def index():
    """Главная страница РГЗ"""
    if 'user_id' not in session:
        return redirect('/rgz/login')
    
    # Разные шаблоны для разных ролей
    if session.get('user_role') == 'manager':
        return render_template('rgz/manager_index.html')
    else:
        return render_template('rgz/client_index.html')

@rgz.route('/login')
def login_page():
    """Страница входа"""
    if 'user_id' in session:
        return redirect('/rgz/')
    return render_template('rgz/login.html')

@rgz.route('/logout')
def logout():
    """Выход"""
    session.clear()
    flash('Вы успешно вышли из системы', 'success')
    return redirect('/rgz/login')

@rgz.route('/profile')
@login_required
def profile():
    """Страница профиля"""
    return render_template('rgz/profile.html')

@rgz.route('/transfer')
@login_required
@client_required
def transfer_page():
    """Страница перевода денег (только для клиентов)"""
    return render_template('rgz/transfer.html')

@rgz.route('/history')
@login_required
def history_page():
    """Страница истории транзакций"""
    return render_template('rgz/history.html')

@rgz.route('/users')
@login_required
@manager_required
def users_page():
    """Страница управления пользователями (только для менеджеров)"""
    return render_template('rgz/users.html')

@rgz.route('/create_user')
@login_required
@manager_required
def create_user_page():
    """Страница создания нового пользователя (только для менеджеров)"""
    return render_template('rgz/create_user.html')

@rgz.route('/statistics')
@login_required
@manager_required
def statistics_page():
    """Страница статистики (только для менеджеров)"""
    return render_template('rgz/statistics.html')

# Добавим обработку JSON для всех ответов
@rgz.after_request
def after_request(response):
    """Добавляем заголовки для JSON ответов"""
    if response.mimetype == 'application/json':
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
    return response

