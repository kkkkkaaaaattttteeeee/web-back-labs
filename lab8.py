from flask import Blueprint, render_template

lab8= Blueprint('lab8', __name__, template_folder='templates/lab8')

@lab8.route('/lab8/')
def index():
    return render_template('lab8/lab8.html')

@lab8.route('/lab8/login')
def login():
    return render_template('lab8/login.html', title="Вход")

@lab8.route('/lab8/register')
def register():
    return render_template('lab8/register.html', title="Регистрация")

@lab8.route('/lab8/articles')
def articles():
    return render_template('lab8/articles.html', title="Список статей")

@lab8.route('/lab8/create')
def create():
    return render_template('lab8/create.html', title="Создать статью")