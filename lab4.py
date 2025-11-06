from flask import Blueprint, request, render_template
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

tree_count=0

@lab4.route('/lab4/tree', methods= ['GET', 'POST'])
def tree():
    global tree_count
    if request.method == 'GET':
        return render_template('lab4/tree.html', tree_count=tree_count)
    
    operation = request.form.get('operation')

    if operation == 'cut':
        tree_count -= 1
    elif operation == 'plant':
        tree_count += 1
    
    return render_template('lab4/tree.html', tree_count=tree_count)