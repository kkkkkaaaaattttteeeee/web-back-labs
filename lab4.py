from flask import Blueprint, request, render_template, redirect, session
lab4 = Blueprint('lab4', __name__)


@lab4.route('/lab4/')
def lab():
    return render_template('lab4/lab4.html')


@lab4.route('/lab4/div-form')
def div_form():
    return render_template('lab4/div-form.html')


@lab4.route('/lab4/div', methods = ['POST'])
def div():
    x1 = request.form.get('x1')
    x2 = request.form.get('x2')
    
    # Проверка на пустые поля
    if x1 == '' or x2 == '':
        return render_template('lab4/div.html', error = 'Оба поля должны быть заполнены')
    
    x1 = int(x1)
    x2 = int(x2)
    
    # Проверка деления на ноль
    if x2 == 0:
        return render_template('lab4/div.html', error = 'Ошибка: деление на ноль невозможно')
    
    result = x1 / x2
    return render_template('lab4/div.html', x1=x1, x2=x2, result=result)


# Суммирование
@lab4.route('/lab4/sum', methods=['GET', 'POST'])
def sum_numbers():
    if request.method == 'POST':
        x1 = request.form.get('x1', '0')  # По умолчанию 0
        x2 = request.form.get('x2', '0')  # По умолчанию 0
        
        x1 = float(x1) if x1 else 0
        x2 = float(x2) if x2 else 0
        
        result = x1 + x2
        return render_template('lab4/sum.html', x1=x1, x2=x2, result=result)
    return render_template('lab4/sum.html')

# Умножение
@lab4.route('/lab4/multiply', methods=['GET', 'POST'])
def multiply():
    if request.method == 'POST':
        x1 = request.form.get('x1', '1')  # По умолчанию 1
        x2 = request.form.get('x2', '1')  # По умолчанию 1
        
        x1 = float(x1) if x1 else 1
        x2 = float(x2) if x2 else 1
        
        result = x1 * x2
        return render_template('lab4/multiply.html', x1=x1, x2=x2, result=result)
    return render_template('lab4/multiply.html')

# Вычитание
@lab4.route('/lab4/subtract', methods=['GET', 'POST'])
def subtract():
    if request.method == 'POST':
        x1 = request.form.get('x1')
        x2 = request.form.get('x2')
        
        if x1 == '' or x2 == '':
            return render_template('lab4/subtract.html', error='Оба поля должны быть заполнены')
        
        x1 = float(x1)
        x2 = float(x2)
        
        result = x1 - x2
        return render_template('lab4/subtract.html', x1=x1, x2=x2, result=result)
    return render_template('lab4/subtract.html')

# Возведение в степень
@lab4.route('/lab4/power', methods=['GET', 'POST'])
def power():
    if request.method == 'POST':
        x1 = request.form.get('x1')
        x2 = request.form.get('x2')
        
        if x1 == '' or x2 == '':
            return render_template('lab4/power.html', error='Оба поля должны быть заполнены')
        
        x1 = float(x1)
        x2 = float(x2)
        
        # Проверка: оба числа не могут быть нулями
        if x1 == 0 and x2 == 0:
            return render_template('lab4/power.html', error='Ошибка: оба числа не могут быть нулями')
        
        result = x1 ** x2
        return render_template('lab4/power.html', x1=x1, x2=x2, result=result)
    return render_template('lab4/power.html')

tree_count = 0  # Инициализация глобальной переменной
MAX_TREES = 10  # Максимальное количество деревьев

@lab4.route('/lab4/tree', methods=['GET', 'POST'])
def tree():
    global tree_count
    if request.method == 'GET':
        return render_template('lab4/tree.html', tree_count=tree_count, max_trees=MAX_TREES)
    
    operation = request.form.get('operation')

    if operation == 'cut':
        # Проверка, чтобы счетчик не ушел в отрицательную область
        if tree_count > 0:
            tree_count -= 1
    elif operation == 'plant':
        # Проверка, чтобы не превысить максимальное количество
        if tree_count < MAX_TREES:
            tree_count += 1
    
    return redirect('/lab4/tree')


# Обновленный список пользователей с дополнительной информацией
users = [
    {'login': 'alex', 'password': '123', 'name': 'Александр Петров', 'gender': 'male'},
    {'login': 'john9977', 'password': 'qwerty', 'name': 'Иван Иванов', 'gender': 'male'},
    {'login': 'mary_smith', 'password': 'password', 'name': 'Мария Сидорова', 'gender': 'female'},
    {'login': 'admin', 'password': 'admin', 'name': 'Администратор', 'gender': 'male'}
]

@lab4.route('/lab4/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if 'login' in session and 'user_name' in session:
            authorized = True
            user_name = session['user_name']
        else:
            authorized = False
            user_name = ''
        return render_template('lab4/login.html', authorized=authorized, user_name=user_name)
    
    login_input = request.form.get('login', '').strip()
    password = request.form.get('password', '').strip()
    
    # Проверка на пустые значения
    if not login_input:
        return render_template('lab4/login.html', error='Не введён логин', login_input=login_input, authorized=False)
    
    if not password:
        return render_template('lab4/login.html', error='Не введён пароль', login_input=login_input, authorized=False)
    
    # Проверка логина и пароля
    for user in users:
        if login_input == user['login'] and password == user['password']:
            session['login'] = user['login']
            session['user_name'] = user['name']  # Сохраняем имя пользователя
            session['gender'] = user['gender']   # Сохраняем пол
            return redirect('/lab4/login')
    
    error = 'Неверные логин и/или пароль'
    return render_template('lab4/login.html', error=error, login_input=login_input, authorized=False)


@lab4.route('/lab4/logout', methods=['POST'])
def logout():
    session.pop('login', None)
    session.pop('user_name', None)
    session.pop('gender', None)
    return redirect('/lab4/login')


@lab4.route('/lab4/fridge', methods=['GET', 'POST'])
def fridge():
    if request.method == 'GET':
        return render_template('lab4/fridge.html')

    temperature = request.form.get('temperature')

    if not temperature:
        return render_template('lab4/fridge.html', error='Ошибка: не задана температура')

    try:
        temp = int(temperature)
    except ValueError:
        return render_template('lab4/fridge.html', error='Ошибка: температура должна быть числом')

    if temp < -12:
        return render_template('lab4/fridge.html', error='Не удалось установить температуру — слишком низкое значение')

    if temp > -1:
        return render_template('lab4/fridge.html', error='Не удалось установить температуру — слишком высокое значение')

    snowflakes = ''
    if -12 <= temp <= -9:
        snowflakes = '***'
    elif -8 <= temp <= -5:
        snowflakes = '**'
    elif -4 <= temp <= -1:
        snowflakes = '*'

    return render_template('lab4/fridge.html', temperature=temp, snowflakes=snowflakes)

