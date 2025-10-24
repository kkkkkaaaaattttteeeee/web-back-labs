from flask import Blueprint, render_template, request, make_response, redirect, url_for
lab3 = Blueprint('lab3', __name__)


@lab3.route('/lab3/cookie')
def cookie():
    resp = make_response(redirect('/lab3/'))
    resp.set_cookie('name', 'Alex', max_age=5)
    resp.set_cookie('age', '20')
    resp.set_cookie('name_color', 'magenta')
    return resp

@lab3.route('/lab3/')
def lab():
    name = request.cookies.get('name')
    name_color = request.cookies.get('name_color')
    age = request.cookies.get('age')
    return render_template('lab3/lab3.html', name=name, name_color=name_color, age=age)


@lab3.route('/lab3/del_cookie')
def del_cookie():
    resp = make_response(redirect('/lab3/'))
    resp.delete_cookie('name')
    resp.delete_cookie('age')
    resp.delete_cookie('name_color')
    return resp


@lab3.route('/lab3/form1')
def form():
    errors = {}
    user = request.args.get('user')
    age = request.args.get('age')
    if user == '':
        errors['user'] = 'Заполните поле!'

    age = request.args.get('age')
    if age == '':
        errors['age'] = 'Заполните поле!'

    sex = request.args.get('sex')
    return render_template('lab3/form1.html', user=user, age=age, sex=sex, errors=errors)


@lab3.route('/lab3/order')
def order():
    return render_template('lab3/order.html')


@lab3.route('/lab3/pay')
def pay():
    price=0
    drink = request.args.get('drink')
    if drink == 'coffee':
        price=120
    elif drink == 'black-tea':
        price = 80
    else:
        price = 70

    if request.args.get('milk') == 'on':
        price +=30
    if request.args.get('sugar') == 'on':
        price += 10

    return render_template('lab3/pay.html', price=price)

@lab3.route('/lab3/success')
def success():
        price = request.args.get('price',0)
        return render_template('lab3/success.html',  price=price)


@lab3.route('/lab3/settings')
def settings():
    # Получаем параметры из GET-запроса
    color = request.args.get('color')
    bg_color = request.args.get('bg_color')
    font_size = request.args.get('font_size')
    font_style = request.args.get('font_style')
    
    # Если есть параметры в запросе - устанавливаем куки
    if any([color, bg_color, font_size, font_style]):
        resp = make_response(redirect(url_for('lab3.settings')))
        if color:
            resp.set_cookie('color', color)
        if bg_color:
            resp.set_cookie('bg_color', bg_color)
        if font_size:
            resp.set_cookie('font_size', font_size)
        if font_style:
            resp.set_cookie('font_style', font_style)
        return resp

    # Получаем значения из куки
    color = request.cookies.get('color')
    bg_color = request.cookies.get('bg_color')
    font_size = request.cookies.get('font_size')
    font_style = request.cookies.get('font_style')
    
    resp = make_response(render_template('lab3/settings.html', 
                                        color=color, 
                                        bg_color=bg_color, 
                                        font_size=font_size, 
                                        font_style=font_style))
    return resp


@lab3.route('/lab3/reset_settings')
def reset_settings():
    resp = make_response(redirect(url_for('lab3.settings')))
    resp.delete_cookie('color')
    resp.delete_cookie('bg_color')
    resp.delete_cookie('font_size')
    resp.delete_cookie('font_style')
    return resp


@lab3.route('/lab3/train')
def train_form():
    return render_template('lab3/train_form.html')

@lab3.route('/lab3/train_ticket')
def train_ticket():
    # Получаем данные из формы
    fio = request.args.get('fio')
    shelf = request.args.get('shelf')
    linen = request.args.get('linen')
    baggage = request.args.get('baggage')
    age = request.args.get('age')
    departure = request.args.get('departure')
    destination = request.args.get('destination')
    date = request.args.get('date')
    insurance = request.args.get('insurance')

    # Проверка на пустые поля
    errors = {}
    if not fio:
        errors['fio'] = 'Заполните ФИО пассажира'
    if not shelf:
        errors['shelf'] = 'Выберите полку'
    if not age:
        errors['age'] = 'Заполните возраст'
    elif not age.isdigit() or not (1 <= int(age) <= 120):
        errors['age'] = 'Возраст должен быть от 1 до 120 лет'
    if not departure:
        errors['departure'] = 'Заполните пункт выезда'
    if not destination:
        errors['destination'] = 'Заполните пункт назначения'
    if not date:
        errors['date'] = 'Выберите дату поездки'

    if errors:
        return render_template('lab3/train_form.html', errors=errors, 
                             fio=fio, shelf=shelf, linen=linen, baggage=baggage,
                             age=age, departure=departure, destination=destination,
                             date=date, insurance=insurance)

    # Расчет стоимости
    if int(age) < 18:
        ticket_type = "Детский билет"
        base_price = 700
    else:
        ticket_type = "Взрослый билет"
        base_price = 1000

    # Доплаты
    additional_cost = 0
    if shelf in ['lower', 'lower-side']:
        additional_cost += 100
    if linen == 'on':
        additional_cost += 75
    if baggage == 'on':
        additional_cost += 250
    if insurance == 'on':
        additional_cost += 150

    total_price = base_price + additional_cost

    return render_template('lab3/train_ticket.html',
                         fio=fio, shelf=shelf, linen=linen, baggage=baggage,
                         age=age, departure=departure, destination=destination,
                         date=date, insurance=insurance, ticket_type=ticket_type,
                         total_price=total_price)


# Список товаров
products = [
    {'name': 'iPhone 15', 'price': 999, 'brand': 'Apple', 'color': 'черный'},
    {'name': 'Samsung Galaxy S24', 'price': 899, 'brand': 'Samsung', 'color': 'белый'},
    {'name': 'Xiaomi Redmi Note 13', 'price': 299, 'brand': 'Xiaomi', 'color': 'синий'},
    {'name': 'Google Pixel 8', 'price': 799, 'brand': 'Google', 'color': 'серый'},
    {'name': 'OnePlus 12', 'price': 699, 'brand': 'OnePlus', 'color': 'зеленый'},
    {'name': 'iPhone 14', 'price': 799, 'brand': 'Apple', 'color': 'красный'},
    {'name': 'Samsung Galaxy A54', 'price': 349, 'brand': 'Samsung', 'color': 'фиолетовый'},
    {'name': 'Xiaomi Poco X6', 'price': 249, 'brand': 'Xiaomi', 'color': 'желтый'},
    {'name': 'Google Pixel 7a', 'price': 499, 'brand': 'Google', 'color': 'черный'},
    {'name': 'OnePlus Nord 3', 'price': 399, 'brand': 'OnePlus', 'color': 'синий'},
    {'name': 'iPhone SE', 'price': 429, 'brand': 'Apple', 'color': 'белый'},
    {'name': 'Samsung Galaxy Z Flip5', 'price': 999, 'brand': 'Samsung', 'color': 'фиолетовый'},
    {'name': 'Xiaomi 13T', 'price': 599, 'brand': 'Xiaomi', 'color': 'черный'},
    {'name': 'Google Pixel Fold', 'price': 1799, 'brand': 'Google', 'color': 'серый'},
    {'name': 'OnePlus Open', 'price': 1699, 'brand': 'OnePlus', 'color': 'зеленый'},
    {'name': 'iPhone 15 Pro', 'price': 1199, 'brand': 'Apple', 'color': 'титан'},
    {'name': 'Samsung Galaxy S23 FE', 'price': 599, 'brand': 'Samsung', 'color': 'синий'},
    {'name': 'Xiaomi Redmi 12', 'price': 179, 'brand': 'Xiaomi', 'color': 'серебристый'},
    {'name': 'Google Pixel 6a', 'price': 349, 'brand': 'Google', 'color': 'зеленый'},
    {'name': 'OnePlus 11', 'price': 799, 'brand': 'OnePlus', 'color': 'черный'}
]

@lab3.route('/lab3/products')
def products_search():
    # Получаем цены из куки или вычисляем
    min_price_cookie = request.cookies.get('min_price')
    max_price_cookie = request.cookies.get('max_price')
    
    # Вычисляем мин и макс цены из всех товаров
    all_prices = [p['price'] for p in products]
    min_all_price = min(all_prices)
    max_all_price = max(all_prices)
    
    # Получаем параметры поиска
    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')
    reset = request.args.get('reset')
    
    # Обработка сброса
    if reset:
        resp = make_response(redirect(url_for('lab3.products_search')))
        resp.delete_cookie('min_price')
        resp.delete_cookie('max_price')
        return resp
    
    # Если есть параметры в запросе - устанавливаем куки
    if min_price is not None or max_price is not None:
        resp = make_response(redirect(url_for('lab3.products_search')))
        if min_price:
            resp.set_cookie('min_price', min_price)
        else:
            resp.delete_cookie('min_price')
        if max_price:
            resp.set_cookie('max_price', max_price)
        else:
            resp.delete_cookie('max_price')
        return resp
    
    # Используем значения из куки для фильтрации
    filtered_products = products
    if min_price_cookie or max_price_cookie:
        min_val = int(min_price_cookie) if min_price_cookie else min_all_price
        max_val = int(max_price_cookie) if max_price_cookie else max_all_price
        
        # Автоматическое исправление если min > max
        if min_val > max_val:
            min_val, max_val = max_val, min_val
        
        filtered_products = [p for p in products if min_val <= p['price'] <= max_val]
        current_min = min_val
        current_max = max_val
    else:
        filtered_products = products
        current_min = ''
        current_max = ''
    
    return render_template('lab3/products.html',
                         products=filtered_products,
                         min_all_price=min_all_price,
                         max_all_price=max_all_price,
                         current_min=current_min,
                         current_max=current_max,
                         products_count=len(filtered_products),
                         all_products_count=len(products))