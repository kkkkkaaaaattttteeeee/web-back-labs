from flask import Flask, url_for, request, redirect
app = Flask(__name__)
from datetime import datetime

@app.route("/")
@app.route("/web")
def start():
    return """<!doctype html>\
        <html>\
           <body>\
                <h1>web-сервер на flask</h1>\
           </body>\
        </html>""",200, {
            'X-Server': 'sample',
            'Content-Type': 'text/plain; charset=utf-8'
        }

@app.route("/author") 
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

@app.route("/image")
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

@app.route("/counter")
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
        </body>
    </html>"""

@app.route("/info")
def info():
    return redirect("/author")

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