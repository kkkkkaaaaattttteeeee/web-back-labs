from flask import Blueprint, request, render_template, redirect, session
lab5 = Blueprint('lab5', __name__)
import psycopg2

@lab5.route('/lab5/')
def lab():
    return render_template('lab5/lab5.html')


@lab5.route('/lab5/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('lab5/register.html')
    
    login = request.form.get('login')
    password = request.form.get('password')

    # ИСПРАВЛЕНА ПРОВЕРКА (было if not (login or password))
    if not login or not password:
        return render_template('lab5/register.html', error='Заполните все поля')
    
    try:
        # ПОДКЛЮЧЕНИЕ К БАЗЕ ДАННЫХ
        conn = psycopg2.connect(
            host='127.0.0.1',
            database='knowledge_base_df',  
            user='obedina_ekaterina_knowledge_base',
            password='123'
        )
        cur = conn.cursor()

        # ИСПРАВЛЕНА SQL-ИНЪЕКЦИЯ (не используйте f-строки!)
        cur.execute("SELECT login FROM users WHERE login = %s", (login,))
        if cur.fetchone():
            cur.close()
            conn.close()
            return render_template('lab5/register.html', error="Такой пользователь уже существует")

        # ИСПРАВЛЕНА SQL-ИНЪЕКЦИЯ И ДОБАВЛЕНО ХЕШИРОВАНИЕ
        from werkzeug.security import generate_password_hash
        hashed_password = generate_password_hash(password)
        
        cur.execute("INSERT INTO users (login, password) VALUES (%s, %s)", 
                   (login, hashed_password))
        conn.commit()
        cur.close()
        conn.close()
        
        return render_template('lab5/success.html', login=login)
        
    except Exception as e:
        return render_template('lab5/register.html', error=f'Ошибка базы данных: {str(e)}')
