from flask import Flask, url_for, request, redirect, render_template, abort
import datetime
import os
from lab1 import lab1
from lab2 import lab2
from lab3 import lab3
from lab4 import lab4
from lab5 import lab5


app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'секретно-секретный секрет')
app.config['DB_TYPE'] = os.getenv('DB_TYPE', 'postgres')


app.register_blueprint(lab1)
app.register_blueprint(lab2)
app.register_blueprint(lab3)
app.register_blueprint(lab4)
app.register_blueprint(lab5)


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
            <li><a href="/lab2">Лабораторная работа 2</a></li>
            <li><a href="/lab3">Лабораторная работа 3</a></li>
            <li><a href="/lab4">Лабораторная работа 4</a></li>
        </ul>
    </nav>
    <footer>
        Обедина Екатерина Сергеевна, Группа ФБИ-33, Курс
    </footer>
</body>
</html>"""



@app.errorhandler(500)
def internal_error(err):
    return render_template('lab1/500.html'), 500



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
        
        return render_template('lab1/404.html', **context), 404
    
    except Exception as e:
        # Fallback если что-то пошло не так
        app.logger.error(f'Error in 404 handler: {e}')
        return render_template('lab1/404.html'), 404
    
    
