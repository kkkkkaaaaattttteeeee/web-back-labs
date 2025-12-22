from flask import Blueprint, request, render_template, redirect, session, current_app, flash, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
import psycopg2
from psycopg2.extras import RealDictCursor
import datetime
import random
import json
from decimal import Decimal

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

def db_connect():
    """Подключение к базе данных"""
    try:
        conn = psycopg2.connect(
            host='127.0.0.1',
            database='bank_db',
            user='obedina_ekaterina_knowledge_base',
            password='123',
            client_encoding='UTF8'
        )
        cur = conn.cursor(cursor_factory=RealDictCursor)
        return conn, cur
    except Exception as e:
        print(f"Database connection error: {e}")
        raise

def db_close(conn, cur):
    """Закрытие соединения с базой данных"""
    try:
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Database close error: {e}")

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
    for key in row.keys():
        result[key] = safe_convert_value(row[key])
    
    return result

def login_required(f):
    """Декоратор для проверки авторизации"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect('/rgz/login')
        return f(*args, **kwargs)
    return decorated_function

def manager_required(f):
    """Декоратор для проверки прав менеджера"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_role' not in session or session['user_role'] != 'manager':
            flash('Доступ только для менеджеров банка', 'error')
            return redirect('/rgz/')
        return f(*args, **kwargs)
    return decorated_function

def client_required(f):
    """Декоратор для проверки прав клиента"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_role' not in session or session['user_role'] != 'client':
            flash('Доступ только для клиентов банка', 'error')
            return redirect('/rgz/')
        return f(*args, **kwargs)
    return decorated_function

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
        
        # Используем параметризованный запрос для PostgreSQL
        cur.execute("SELECT * FROM rgz_users WHERE login = %s", (login,))
        user_row = cur.fetchone()
        
        if not user_row:
            db_close(conn, cur)
            return jsonify({'error': 'Пользователь не найден'}), 401
        
        user = convert_to_dict(user_row)
        stored_password = user.get('password', '')
        
        # Проверяем пароль в зависимости от его формата
        password_correct = False
        
        # Если пароль хранится как хеш scrypt (начинается с scrypt:)
        if stored_password and stored_password.startswith('scrypt:'):
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
        
        # Получаем данные отправителя
        cur.execute("SELECT * FROM rgz_users WHERE id = %s;", (session['user_id'],))
        sender = convert_to_dict(cur.fetchone())
        
        if not sender:
            db_close(conn, cur)
            return jsonify({'error': 'Отправитель не найден'}), 404
        
        if sender.get('balance', 0) < amount:
            db_close(conn, cur)
            return jsonify({'error': 'Недостаточно средств'}), 400
        
        # Ищем получателя по номеру счета или телефону
        cur.execute("""
            SELECT * FROM rgz_users 
            WHERE (account_number = %s OR phone = %s) 
            AND role = 'client';
        """, (to_account, to_account))
        receiver = cur.fetchone()
        
        if not receiver:
            db_close(conn, cur)
            return jsonify({'error': 'Получатель не найден'}), 404
        
        receiver = convert_to_dict(receiver)
        
        if receiver['id'] == sender['id']:
            db_close(conn, cur)
            return jsonify({'error': 'Нельзя перевести себе'}), 400
        
        # Выполняем перевод
        cur.execute("""
            UPDATE rgz_users SET balance = balance - %s 
            WHERE id = %s;
        """, (amount, sender['id']))
        
        cur.execute("""
            UPDATE rgz_users SET balance = balance + %s 
            WHERE id = %s;
        """, (amount, receiver['id']))
        
        # Записываем транзакцию и получаем её ID
        cur.execute("""
            INSERT INTO rgz_transactions 
            (from_account, to_account, amount, description) 
            VALUES (%s, %s, %s, %s)
            RETURNING id;
        """, (sender.get('account_number'), receiver['account_number'], amount, description))
        
        transaction_id = cur.fetchone()['id']
        
        # Получаем обновленный баланс отправителя
        cur.execute("SELECT balance FROM rgz_users WHERE id = %s;", (sender['id'],))
        new_balance = cur.fetchone()['balance']
        
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
        
        if session.get('user_role') == 'client':
            user_account = session.get('user_account')
            cur.execute("""
                SELECT t.*, 
                       u1.full_name as from_name,
                       u2.full_name as to_name
                FROM rgz_transactions t
                LEFT JOIN rgz_users u1 ON t.from_account = u1.account_number
                LEFT JOIN rgz_users u2 ON t.to_account = u2.account_number
                WHERE t.from_account = %s OR t.to_account = %s 
                ORDER BY t.transaction_date DESC;
            """, (user_account, user_account))
        else:
            cur.execute("""
                SELECT t.*, 
                       u1.full_name as from_name,
                       u2.full_name as to_name
                FROM rgz_transactions t
                LEFT JOIN rgz_users u1 ON t.from_account = u1.account_number
                LEFT JOIN rgz_users u2 ON t.to_account = u2.account_number
                ORDER BY t.transaction_date DESC;
            """)
        
        transactions = []
        for row in cur.fetchall():
            transaction = convert_to_dict(row)
            # Добавляем отформатированную дату для удобства
            if transaction.get('transaction_date'):
                try:
                    if isinstance(transaction['transaction_date'], str):
                        # Если дата в строковом формате
                        for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S.%f', '%Y-%m-%d %H:%M:%S.%f']:
                            try:
                                dt = datetime.datetime.strptime(transaction['transaction_date'], fmt)
                                transaction['formatted_date'] = dt.strftime('%d.%m.%Y %H:%M')
                                break
                            except:
                                continue
                    else:
                        # Если это datetime объект
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
        cur.execute("""
            SELECT id, login, full_name, phone, account_number, 
                   COALESCE(balance, 0) as balance, role, 
                   DATE(created_at) as created_date
            FROM rgz_users 
            ORDER BY role, full_name;
        """)
        
        users = []
        for row in cur.fetchall():
            user = convert_to_dict(row)
            # Гарантируем что balance это float
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
        
        # Проверяем уникальность логина
        cur.execute("SELECT id FROM rgz_users WHERE login = %s;", (data['login'],))
        if cur.fetchone():
            db_close(conn, cur)
            return jsonify({'error': 'Пользователь с таким логином уже существует'}), 400
        
        # Всегда хешируем пароль при создании
        hashed_password = generate_password_hash(data['password'], method='scrypt')
        
        if data['role'] == 'client':
            # Для клиента нужен номер счета и начальный баланс
            phone = data.get('phone', '')
            if not phone:
                db_close(conn, cur)
                return jsonify({'error': 'Для клиента обязателен телефон'}), 400
            
            # Генерируем уникальный номер счета
            account_number = f'40817810{random.randint(1000000000, 9999999999)}'
            
            # Проверяем уникальность номера счета
            cur.execute("SELECT id FROM rgz_users WHERE account_number = %s;", (account_number,))
            if cur.fetchone():
                account_number = f'40817810{random.randint(1000000000, 9999999999)}'
            
            balance = float(data.get('balance', 10000.00))
            
            cur.execute("""
                INSERT INTO rgz_users 
                (login, password, full_name, phone, account_number, balance, role) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id;
            """, (
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
            cur.execute("""
                INSERT INTO rgz_users 
                (login, password, full_name, role) 
                VALUES (%s, %s, %s, %s)
                RETURNING id;
            """, (
                data['login'],
                hashed_password,
                data['full_name'],
                'manager'
            ))
        
        new_user_id = cur.fetchone()['id']
        
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
        
        # Получаем текущие данные пользователя
        cur.execute("SELECT * FROM rgz_users WHERE id = %s;", (user_id,))
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
            
            cur.execute("""
                UPDATE rgz_users 
                SET full_name = %s, phone = %s, balance = %s 
                WHERE id = %s;
            """, (full_name, phone, balance, user_id))
        else:
            full_name = data.get('full_name', user['full_name'])
            cur.execute("""
                UPDATE rgz_users 
                SET full_name = %s 
                WHERE id = %s;
            """, (full_name, user_id))
        
        # Если нужно обновить пароль
        if data.get('new_password'):
            hashed_password = generate_password_hash(data['new_password'], method='scrypt')
            cur.execute("""
                UPDATE rgz_users 
                SET password = %s 
                WHERE id = %s;
            """, (hashed_password, user_id))
        
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
        
        # Проверяем, что пользователь существует
        cur.execute("SELECT * FROM rgz_users WHERE id = %s;", (user_id,))
        user_row = cur.fetchone()
        
        if not user_row:
            db_close(conn, cur)
            return jsonify({'error': 'Пользователь не найден'}), 404
        
        user = convert_to_dict(user_row)
        
        # Удаляем связанные транзакции пользователя (если он клиент)
        if user.get('role') == 'client' and user.get('account_number'):
            cur.execute("DELETE FROM rgz_transactions WHERE from_account = %s OR to_account = %s;", 
                       (user['account_number'], user['account_number']))
        
        # Удаляем пользователя
        cur.execute("DELETE FROM rgz_users WHERE id = %s;", (user_id,))
        
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
        cur.execute("SELECT * FROM rgz_users WHERE id = %s;", (session['user_id'],))
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
        
        # Основная статистика
        cur.execute("SELECT COUNT(*) as total_users FROM rgz_users;")
        total_users = cur.fetchone()['total_users']
        
        cur.execute("SELECT COUNT(*) as total_clients FROM rgz_users WHERE role = 'client';")
        total_clients = cur.fetchone()['total_clients']
        
        cur.execute("SELECT COUNT(*) as total_managers FROM rgz_users WHERE role = 'manager';")
        total_managers = cur.fetchone()['total_managers']
        
        cur.execute("SELECT COALESCE(SUM(balance), 0) as total_balance FROM rgz_users WHERE role = 'client';")
        total_balance_result = cur.fetchone()['total_balance']
        total_balance = float(total_balance_result) if total_balance_result else 0.0
        
        cur.execute("SELECT COUNT(*) as total_transactions FROM rgz_transactions;")
        total_transactions = cur.fetchone()['total_transactions']
        
        # Статистика по активным пользователям
        cur.execute("""
            SELECT COUNT(DISTINCT u.id) as active_clients
            FROM rgz_users u
            WHERE u.role = 'client' AND EXISTS (
                SELECT 1 FROM rgz_transactions t 
                WHERE t.from_account = u.account_number OR t.to_account = u.account_number
            );
        """)
        active_clients = cur.fetchone()['active_clients']
        
        # Статистика по транзакциям за последние 7 дней
        cur.execute("""
            SELECT 
                DATE(transaction_date) as date,
                COUNT(*) as transactions_count,
                SUM(amount) as total_amount
            FROM rgz_transactions 
            WHERE transaction_date >= CURRENT_DATE - INTERVAL '7 days'
            GROUP BY DATE(transaction_date)
            ORDER BY date;
        """)
        
        weekly_stats = []
        for row in cur.fetchall():
            stats = convert_to_dict(row)
            weekly_stats.append(stats)
        
        # Топ 5 клиентов по балансу
        cur.execute("""
            SELECT full_name, balance 
            FROM rgz_users 
            WHERE role = 'client' 
            ORDER BY balance DESC 
            LIMIT 5;
        """)
        
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