from flask import Blueprint, url_for, redirect, request
lab1 = Blueprint('lab1', __name__)
import datetime


@lab1.route("/lab1")
def lab():
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
        Обедина Екатерина Сергеевна, Группа ФБИ-33, Курс 3
    </footer>
</body>
</html>"""


@lab1.route("/lab1/web")
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


@lab1.route("/lab1/author") 
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
               <a href="/lab1/web">web</a> 
           </body> 
        </html>""" 


@lab1.route("/lab1/image")
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


@lab1.route("/lab1/counter")
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


@lab1.route("/lab1/info")
def info():
    return redirect("/lab1/author")


@lab1.route('/reset_counter')
def reset_counter():
    global count
    count = 0
    return redirect(url_for('counter'))


@lab1.route("/create")
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


@lab1.route('/400')
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


@lab1.route('/401')
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


@lab1.route('/402')
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


@lab1.route('/403')
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


@lab1.route('/405')
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


@lab1.route('/418')
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

