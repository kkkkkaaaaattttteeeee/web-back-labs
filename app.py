from flask import Flask, url_for, request, redirect, render_template, abort
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
        return "цветок: " + flower_list[flower_id]
    
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
    gruppa = 33
    nomer = 2
    nomer_cursa = 3
    return render_template('example.html', name=name, gruppa=gruppa, nomer=nomer, nomer_cursa=nomer_cursa)
