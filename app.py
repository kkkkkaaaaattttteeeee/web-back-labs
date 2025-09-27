from flask import Flask, url_for, request, redirect
app = Flask(__name__)
from datetime import datetime

@app.route("/lab1")
def ones():
    return""" <!doctype html>
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
        </ul>
    </nav>
    <a href="/index">Вернуться назад</a>
    <footer>
        Обедина Екатерина Сергеевна, Группа ФБИ-33, Курс
    </footer>
</body>
</html>"""

@app.route("/")
@app.route("/index")
def index():
    return""" <!doctype html>
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
            'Content-Type': 'text/plain; charset=utf-8'
        }

@app.route("/lab1/author") 
def author(): 
 
    name = "Обедина Екатерина Сергеевна" 
    group = "ФБИ-33" 
    faculty = "ФБ" 
 
    return"""<!doctype html> 
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

    path = url_for("static", filename= "oak.jpg")
    css_path = url_for("static", filename="lab1.css")

    return"""<!doctype html>
        <html>
        <head>
          <title>Самое доброе дерево?</title>
          <link rel="stylesheet" href= """+ css_path +""">
      </head>
           <body>
               <h1>Дуб</h1>
               <img src=""" + path + """>
           </body>
        </html>"""

count=0

@app.route("/lab1/counter")
def counter():
    global count
    time = datetime.today()
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
            <a href = """ + url_for('reset_counter') +""">Сбросить счетчик</a>
        </body>
    </html>"""

@app.route('/reset_counter')
def reset_counter():
    global count
    count=0
    return redirect(url_for('counter'))

@app.route("/lab1/info")
def info():
    return redirect("/lab1/author")

@app.route("/create")
def created():
    return'''
<!doctype html>
    <html>
        <body>
            <h1>Создано успешно!</h1>
            <div><i>Что-то создано...</i></div>
        </body>
    </html>
''', 201

@app.errorhandler(404)
def not_found(err):
    return "Такой страницы нет!"

@app.errorhandler(500)
def internal_error(err):
    return "Внутреняя ошибка сервера",500