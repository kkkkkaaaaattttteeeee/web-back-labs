from flask import Flask, url_for
app = Flask(__name__)

@app.route("/")
@app.route("/web")
def start():
    return """<!doctype html>\
        <html>\
           <body>\
                <h1>web-сервер на flask</h1>\
           </body>\
        </html>"""

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

    return"""<!doctype html>
        <html>
           <body>
               <h1>Дуб</h1>
               <img src="'' + path + ''">
           </body>
        </html>"""