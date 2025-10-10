from flask import Flask, url_for, request, redirect, render_template, abort, render_template_string
import datetime

app = Flask(__name__)

@app.route("/lab1")
def ones():
    return """ <!doctype html>
    <html> 
        <head>
        <title>НГТУ, ФБ, Лабораторная работа 1</title>
        </head>
    <body>
        <header>
            <h1>Лабораторная работа 1</h1>
        </header>
        <div>Flask — фреймворк для создания веб-приложений на языке
программирования Python, использующий набор инструментов
Werkzeug, а также шаблонизатор Jinja2. Относится к категории так
называемых микрофреймворков — минималистичных каркасов
веб-приложений, сознательно предоставляющих лишь самые ба-
зовые возможности.</div>
        <h2>Выполненные задания</h1>
    <nav>
        <ul>
            <li><a href="/lab1/web">Web-сервер на flask</a></li>
            <li><a href="/lab1/author">Автор</a></li>
            <li><a href="/lab1/image">Картинка</a></li>
            <li><a href="/lab1/counter">Счетчик</a></li>
            <li><a href="/lab1/info">Перенаправление</a></li>
            <li><a href="/400">Ошибка 400</a></li>
            <li><a href="/401">Ошибка 401</a></li>
            <li><a href="/402">Ошибка 402</a></li>
            <li><a href="/403">Ошибка 403</a></li>
            <li><a href="/405">Ошибка 405</a></li>
            <li><a href="/418">Ошибка 418</a></li>
        </ul>
    </nav>
    <a href="/index">Верниться назад</a>
    <footer>
        Обедина Екатерина Сергеевна, Группа ФБИ-33, Курс
    </footer>
</body>
</html>"""

@app.route("/")
@app.route("/index")
def index():
    return """ <!doctype html>
    <html> 
        <head>
        <title>НГТУ, ФБ, Лабораторные работы</title>
        </head>
    <body>
        <header>
            <h1>НГТУ, ФБ, WEB-программирование, часть 2. Список лабораторных</h1>
        </header>
    <nav>
        <ul>
            <li><a href="/lab1">Лабораторная работа 1</a></li>
        </ul>
    </nav>
    <footer>
        Обедина Екатерина Сергеевна, Группа ФБИ-33, Курс
    </footer>
</body>
</html>"""

@app.route("/lab1/web")
def start():
    return """
    <!doctype html>\
        <html>\
           <body>\
                <h1>web-сервер на flask</h1>\
           </body>\
        </html>""", 200, {
            'X-Server': 'sample',
            'Content-Type': 'text/plain; charset=UTF-8'
        }

@app.route("/lab1/author") 
def author(): 
    name = "Обедина Екатерина Сергеевна" 
    group = "ФБИ-33" 
    faculty = "ФБ" 
    return """<!doctype html> 
        <html> 
           <body> 
               <p>Студент: """ + name + """</p> 
               <p>Группа: """ + group + """</p> 
               <p>Факультет: """ + faculty + """</p> 
               <a href="/web">web</a> 
           </body> 
        </html>""" 

@app.route("/lab1/image")
def image():
    path = url_for("static", filename="oak.jpg")
    css_path = url_for("static", filename="lab1.css")
    return """<!doctype html>
        <html>
        <head>
          <title>Самое доброе дерево?</title>
          <link rel="stylesheet" href=""" + css_path + """>
      </head>
           <body>
               <h1>Дуб</h1>
               <img src=""" + path + """>
           </body>
        </html>""", 200, {
        'Content-Language': 'ru',
        'X-Trees':'oak',
        'X-Server-Technology': 'Flask Python Framework',
        'Content-Type':'text/html; charset=utf-8'
    }

count = 0

@app.route("/lab1/counter")
def counter():
    global count
    time = datetime.datetime.now()
    url = request.url
    client_ip = request.remote_addr
    count += 1
    return """
<!doctype html>
    <html>
        <body>
            Сколько раз вы сюда заходили: """ + str(count) + """
            <hr>
            Дата и время: """ + str(time) + """
            <br> Запрошенный адрес: """ + url + """
            <br> Ваш IP адрес: """ + client_ip + """
            <a href = """ + url_for('reset_counter') + """>Сбросить счетчик</a>
        </body>
    </html>"""

@app.route('/reset_counter')
def reset_counter():
    global count
    count = 0
    return redirect(url_for('counter'))

@app.route("/lab1/info")
def info():
    return redirect("/lab1/author")

@app.route("/create")
def created():
    return '''
<!doctype html>
    <html>
        <body>
            <h1>Создано успешно!</h1>
            <div><i>Что-то создано...</i></div>
        </body>
    </html>
''', 201

@app.errorhandler(500)
def internal_error(err):
    return render_template('500.html'), 500

@app.route('/400')
def bad_request():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>400 Bad Request</title>
</head>
<body>
<h1>400 Bad Request</h1>
<p>Запрос некорректен или неправильно сформирован.</p>
</body>
</html>
""", 400

@app.route('/401')
def unauthorized():
    return """ <!doctype html>
    <html>
    <head>
    <title>401 Unauthorized</title>
    </head>
    <body>
    <h1>401 Unauthorized</h1>
    <p>Требуется аунтефикация для доступа к ресурсу.</p>
    </body>
    </html>""", 401

@app.route('/402')
def payment_required():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>402 Payment Required</title>
</head>
<body>
<h1>402 Payment Required</h1>
<p>Для продолжения операции необходима оплата.</p>
</body>
</html>
""", 402

@app.route('/403')
def forbidden():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>403 Forbidden</title>
</head>
<body>
<h1>403 Forbidden</h1>
<p>Доступ запрещён. У вас недостаточно прав для просмотра ресурса.</p>
</body>
</html>
""", 403

@app.route('/405')
def method_not_allowed():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>405 Method Not Allowed</title>
</head>
<body>
<h1>405 Method Not Allowed</h1>
<p>Используемый метод HTTP-запроса не поддерживается данным ресурсом.</p>
</body>
</html>
""", 405

@app.route('/418')
def im_a_teapot():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>418 I'm a Teapot</title>
</head>
<body>
<h1>418 I'm a Teapot</h1>
<p>Этот сервер является чайником и не способен заваривать кофе.</p>
</body>
</html>
""", 418

@app.errorhandler(404)
def not_found(err):
    try:
        # Получаем данные пользователя
        user_ip = request.remote_addr
        access_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        accessed_page = request.url
        
        # Логируем доступ
        log_entry = f'{access_time}: {user_ip} попытался зайти на "{accessed_page}".'
        
        with open('access_log.txt', 'a', encoding='utf-8') as log_file:
            log_file.write(f'{log_entry}\n')
        
        # Читаем полный лог для отображения
        log_entries = []
        try:
            with open('access_log.txt', 'r', encoding='utf-8') as log_file:
                log_entries = log_file.read().strip().split('\n')
        except FileNotFoundError:
            pass
        
        # Передаем данные в шаблон
        context = {
            'ip_address': user_ip,
            'access_time': access_time,
            'home_link': '/',
            'log_entries': log_entries
        }
        
        return render_template('404.html', **context), 404
    
    except Exception as e:
        # Fallback если что-то пошло не так
        app.logger.error(f'Error in 404 handler: {e}')
        return render_template('404.html'), 404
    
@app.route('/lab2/a')
def a():
    return 'без слеша'

@app.route('/lab2/a/')
def a2():
    return 'со слешом'

flower_list = ['роза','тюльпан', 'незаудка', 'ромашка']

@app.route('/lab2/flowers/<int:flower_id>')
def flowers(flower_id):
    if flower_id >= len(flower_list):
        abort(404)
    else:
        flower_name = flower_list[flower_id]
        html = f'''
        <!doctype html>
        <html>
            <head>
                <title>Цветок #{flower_id}</title>
            </head>
            <body>
                <h1>Информация о цветке</h1>
                <p><strong>ID цветка:</strong> {flower_id}</p>
                <p><strong>Название:</strong> {flower_name}</p>
                <p><strong>Всего цветков в базе:</strong> {len(flower_list)}</p>
                <br>
                <a href="/lab2/all_flowers">Посмотреть все цветы</a><br>
                <a href="/lab2">На главную</a>
            </body>
        </html>
        '''
        return html 
    
@app.route('/lab2/add_flower/<name>')
def add_flower(name):
    flower_list.append(name)
    return f'''
<!doctype html>
<html>
    <body>
    <h1>Добавлен новый цветок</h1>
    <p>Название нового цветка: {name} </p>
    <p> Всего цветков: {len(flower_list)} </p>
    <p>Полный список: {flower_list} </p>
    </body>
</html>
'''

@app.route('/lab2/example')
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

@app.route('/lab2/')
def lab2():
    return render_template('lab2.html')

@app. route('/lab2/filters')
def filters() :
    phrase = "0 <b>сколько</b> <u>нам</u≥ <i>открытий</i> чудных..."
    return render_template('filter.html', phrase = phrase)

@app.route('/lab2/add_flower/')
def add_flower_empty():
    abort(400, "вы не задали имя цветка")

@app.route('/lab2/all_flowers')
def all_flowers():
    html = '''
    <!doctype html>
    <html>
        <head>
            <title>Все цветы</title>
        </head>
        <body>
            <h1>Список всех цветов</h1>
            <p><strong>Всего цветков:</strong> {count}</p>
            <h2>Список:</h2>
            <ul>
    '''.format(count=len(flower_list))
    
    for i, flower in enumerate(flower_list):
        html += f'<li>{i}: {flower}</li>\n'
    
    html += '''
            </ul>
            <br>
            <a href="/lab2/clear_flowers">Очистить список цветов</a><br>
            <a href="/lab2">На главную</a>
        </body>
    </html>
    '''
    return html

@app.route('/lab2/clear_flowers')
def clear_flowers():
    flower_list.clear()
    return '''
    <!doctype html>
    <html>
        <head>
            <title>Список очищен</title>
        </head>
        <body>
            <h1>Список цветов очищен</h1>
            <p>Все цветы были удалены из списка.</p>
            <br>
            <a href="/lab2/all_flowers">Посмотреть все цветы</a><br>
            <a href="/lab2">На главную</a>
        </body>
    </html>
    '''
@app.route('/lab2/calc/<int:a>/<int:b>')
def calculator(a, b):
    result = f"""a = {a}, b = {b}
{a} + {b} = {a + b}
{a} - {b} = {a - b}
{a} * {b} = {a * b}
{a} / {b} = {a / b}
{a} ** {b} = {a ** b}"""
    return result.replace('\n', '<br>')

@app.route('/lab2/calc/')
def calc_default():
    return redirect('/lab2/calc/1/1')

@app.route('/lab2/calc/<int:a>')
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

@app.route('/lab2/books')
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

@app.route('/lab2/berries')
def show_berries():
    return render_template('berries.html', berries=berries)