from flask import Blueprint, url_for, redirect, request, render_template, abort
lab2 = Blueprint('lab2', __name__)


@lab2.route('/lab2/a')
def a():
    return 'без слеша'

@lab2.route('/lab2/a/')
def a2():
    return 'со слешом'

flower_list = [
    {'name': 'роза', 'price': 150},
    {'name': 'тюльпан', 'price': 80},
    {'name': 'незабудка', 'price': 50},
    {'name': 'ромашка', 'price': 40},
]

@lab2.route('/lab2/all_flowers')
def all_flowers():
    return render_template('all_flowers.html', flowers=flower_list)


@lab2.route('/lab2/flowers/<int:flower_id>')
def flower_detail(flower_id):
    if flower_id >= len(flower_list):
        return f"Цветок с ID {flower_id} не найден", 404
    
    flower = flower_list[flower_id]
    
    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Цветок #{flower_id}</title>
        <link rel="icon" type="image/x-icon" href="/static/favicon.ico">
    </head>
    <body>
        <h1>🌸 Цветок {flower_id}</h1>
        
        <p><strong>Название:</strong> {flower['name']}</p>
        <p><strong>Цена:</strong> {flower['price']} руб.</p>
        
        <br>
        <a href="/lab2/all_flowers">← Назад к списку цветов</a><br>
        <a href="/lab2/">← Назад к лабораторной работе</a><br>
        <a href="/">← На главную</a>
        
        <br><br>
        <small>Всего цветов: {len(flower_list)}</small>
    </body>
    </html>
    '''
    return html
    

@lab2.route('/lab2/example')
def example():
    name = 'Екатерина Обедина'
    nomer = 2
    nomer_cursa = 3
    fruits = [
        {'name': 'яблоки', 'price': 100},
        {'name': 'груши', 'price': 120},
        {'name': 'апельсины', 'price': 80},
        {'name': 'мандарины', 'price': 95},
        {'name': 'манго', 'price': 321}
    ]
    return render_template('example.html', name=name, nomer=nomer, nomer_cursa=nomer_cursa, fruits=fruits)


@lab2.route('/lab2/')
def lab():
    return """ <!doctype html>
    <html> 
        <head>
        <title>НГТУ, ФБ, Лабораторная работа 2</title>
        </head>
    <body>
        <header>
            <h1>Лабораторная работа 2</h1>
        </header>
        <h2>Выполненные задания</h1>
    <nav>
        <ul>
            <li><a href="/lab2/flowers/2">Работа с цветами, добавление и очистка</a></li>
            <li><a href="/lab2/example">Использование шаблонов, подключение стилей, условия и циклы </a></li>
            <li><a href="/lab2/filters">Фильтры</a></li>
            <li><a href="/lab2/calc">Подсчет</a></li>
            <li><a href="/lab2/books">Книги</a></li>
            <li><a href="/lab2/berries">Ягоды </a></li>
            <li><a href="/lab2/all_flowers">Дополнительное задание</a></li>
        </ul>
    </nav>
    <a href="/index">Вернуться назад</a>
    <footer>
        Обедина Екатерина Сергеевна, Группа ФБИ-33, Курс
    </footer>
</body>
</html>"""


@lab2.route('/lab2/filters')
def filter() :
    phrase = "0 <b>сколько</b> <u>нам</u≥ <i>открытий</i> чудных..."
    return render_template('filter.html', phrase = phrase)


@lab2.route('/lab2/add_flower', methods=['POST'])
def add_flower_form():
    name = request.form.get('name')
    price = request.form.get('price', 0)
    if name:
        flower_list.append({'name': name, 'price': int(price)})
    return redirect(url_for('lab2.all_flowers'))


@lab2.route('/lab2/add_flower/<name>')
def add_flower_old(name):
    flower_list.append({'name': name, 'price': 0})
    return redirect(url_for('lab2.all_flowers'))  


@lab2.route('/lab2/clear_flowers')
def clear_flowers():
    flower_list.clear()
    return redirect(url_for('lab2.all_flowers')) 


@lab2.route('/lab2/calc/<int:a>/<int:b>')
def calculator(a, b):
    result = f"""a = {a}, b = {b}
{a} + {b} = {a + b}
{a} - {b} = {a - b}
{a} * {b} = {a * b}
{a} / {b} = {a / b}
{a} ** {b} = {a ** b}"""
    return result.replace('\n', '<br>')

@lab2.route('/lab2/calc/')
def calc_default():
    return redirect('/lab2/calc/1/1')

@lab2.route('/lab2/calc/<int:a>')
def calc_single_number(a):
    return redirect(f'/lab2/calc/{a}/1')

books = [
    {"author": "Фёдор Достоевский", "title": "Преступление и наказание", "genre": "Роман", "pages": 671},
    {"author": "Лев Толстой", "title": "Война и мир", "genre": "Роман-эпопея", "pages": 1225},
    {"author": "Михаил Булгаков", "title": "Мастер и Маргарита", "genre": "Роман", "pages": 480},
    {"author": "Антон Чехов", "title": "Рассказы", "genre": "Рассказы", "pages": 320},
    {"author": "Александр Пушкин", "title": "Евгений Онегин", "genre": "Роман в стихах", "pages": 240},
    {"author": "Николай Гоголь", "title": "Мёртвые души", "genre": "Поэма", "pages": 352},
    {"author": "Иван Тургенев", "title": "Отцы и дети", "genre": "Роман", "pages": 288},
    {"author": "Александр Островский", "title": "Гроза", "genre": "Драма", "pages": 120},
    {"author": "Михаил Лермонтов", "title": "Герой нашего времени", "genre": "Роман", "pages": 224},
    {"author": "Иван Гончаров", "title": "Обломов", "genre": "Роман", "pages": 576}
]

@lab2.route('/lab2/books')
def show_books():
    return render_template('books.html', books=books)

berries = [
    {"name": "Клубника", "image": "strawberry.jpg", "description": "Сладкая красная ягода, богатая витамином C"},
    {"name": "Малина", "image": "raspberry.jpg", "description": "Ароматная ягода, часто используется в десертах"},
    {"name": "Черника", "image": "blueberry.jpg", "description": "Маленькая синяя ягода, полезна для зрения"},
    {"name": "Ежевика", "image": "blackberry.jpg", "description": "Тёмная ягода с кисло-сладким вкусом"},
    {"name": "Смородина", "image": "currant.jpg", "description": "Бывает чёрная, красная и белая, богата витаминами"},
    {"name": "Крыжовник", "image": "gooseberry.jpg", "description": "Зелёная ягода с характерным кисловатым вкусом"},
    {"name": "Земляника", "image": "wild_strawberry.jpg", "description": "Лесная ягода с насыщенным ароматом"},
    {"name": "Брусника", "image": "lingonberry.jpg", "description": "Красная ягода с горьковатым привкусом"},
    {"name": "Клюква", "image": "cranberry.jpg", "description": "Кислая ягода, растущая на болотах"},
    {"name": "Облепиха", "image": "sea_buckthorn.jpg", "description": "Оранжевая ягода с высоким содержанием масел"},
    {"name": "Голубика", "image": "bilberry.jpg", "description": "Лесная ягода, похожая на чернику"},
    {"name": "Шиповник", "image": "rose_hip.jpg", "description": "Плоды розы, богатые витамином C"},
    {"name": "Боярышник", "image": "hawthorn.jpg", "description": "Красные ягоды, полезные для сердца"},
    {"name": "Ирга", "image": "serviceberry.jpg", "description": "Сладкие синие ягоды, растущие на кустах"},
    {"name": "Калина", "image": "viburnum.jpg", "description": "Красные горькие ягоды, используются в народной медицине"},
    {"name": "Рябина", "image": "rowan.jpg", "description": "Оранжево-красные ягоды, становятся сладкими после заморозков"},
    {"name": "Черёмуха", "image": "bird_cherry.jpg", "description": "Чёрные ароматные ягоды с вяжущим вкусом"},
    {"name": "Арония", "image": "chokeberry.jpg", "description": "Чёрноплодная рябина, богатая антиоксидантами"},
    {"name": "Жимолость", "image": "honeysuckle.jpg", "description": "Синие продолговатые ягоды с уникальным вкусом"},
    {"name": "Виноград", "image": "grape.jpg", "description": "Сочные ягоды, используемые для еды и производства вина"}
]

@lab2.route('/lab2/berries')
def show_berries():
    return render_template('berries.html', berries=berries)

@lab2.route('/lab2/delete_flower/<int:flower_id>')
def delete_flower(flower_id):
    if flower_id >= len(flower_list):
        abort(404)
    flower_list.pop(flower_id)
    return redirect(url_for('lab2.all_flowers'))