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


users = [
    {'login': 'alex', 'password': '123'},
    {'login': 'bob', 'password': '555'},
    {'login': 'kate', 'password': '666'}
]

@lab4.route('/lab4/login', methods = ['GET', 'POST'])
def login ():
    if request.method == 'GET':
        if 'login' in session:
            authorized = True
            login = session['login']
        else:
            authorized = False
            login = ''
        return render_template('lab4/login.html', authorized=authorized, login=login)
    login = request.form.get('login')
    password = request.form.get('password')

    for user in users:
        if login == user['login'] and password == user['password']:
            session['login'] = login
            return redirect('/lab4/login')
    
    error = 'Неверные логин и/или пароль'
    return render_template('lab4/login.html', error=error, authorized=False)


@lab4.route('/lab4/logout', methods = ['POST'])
def logout():
    session.pop('login', None)
    return redirect('/lab4/login')