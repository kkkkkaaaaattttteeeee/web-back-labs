from flask import Blueprint, render_template, session, jsonify, request
import random
import json
import os

lab9 = Blueprint('lab9', __name__)

# Хранилище для открытых коробок (в памяти)
opened_boxes = set()

# Поздравления и подарки для каждой коробки (коробки 7-10 только для авторизованных)
BOX_DATA = [
    {"id": 1, "congratulation": "С Новым годом! Пусть сбудутся все мечты!", "gift": "/static/gifts/gift1.png", "premium": False},
    {"id": 2, "congratulation": "Желаю здоровья и счастья в новом году!", "gift": "/static/gifts/gift2.png", "premium": False},
    {"id": 3, "congratulation": "Пусть новый год принесет много радости!", "gift": "/static/gifts/gift3.png", "premium": False},
    {"id": 4, "congratulation": "Желаю успехов во всех начинаниях!", "gift": "/static/gifts/gift4.png", "premium": False},
    {"id": 5, "congratulation": "Пусть год будет полон приятных сюрпризов!", "gift": "/static/gifts/gift5.png", "premium": False},
    {"id": 6, "congratulation": "Счастья, любви и процветания!", "gift": "/static/gifts/gift6.png", "premium": False},
    {"id": 7, "congratulation": "Мечтайте, верьте, добивайтесь целей!", "gift": "/static/gifts/gift7.png", "premium": True},
    {"id": 8, "congratulation": "Пусть каждый день дарит улыбки!", "gift": "/static/gifts/gift8.png", "premium": True},
    {"id": 9, "congratulation": "Новых достижений и побед!", "gift": "/static/gifts/gift9.png", "premium": True},
    {"id": 10, "congratulation": "Мира, добра и тепла в вашем доме!", "gift": "/static/gifts/gift10.png", "premium": True}
]

# Фиксированные позиции для коробок
if not os.path.exists('box_positions.json'):
    positions = []
    for i in range(10):
        positions.append({
            "top": random.randint(5, 70),
            "left": random.randint(5, 70),
            "rotation": random.randint(-15, 15)
        })
    with open('box_positions.json', 'w') as f:
        json.dump(positions, f)

with open('box_positions.json', 'r') as f:
    BOX_POSITIONS = json.load(f)

@lab9.route('/lab9/')
def main():
    # Инициализируем сессию
    if 'opened_count' not in session:
        session['opened_count'] = 0
    if 'opened_by_user' not in session:
        session['opened_by_user'] = []
    
    remaining_boxes = 10 - len(opened_boxes)
    is_authenticated = session.get('authenticated', False)
    
    return render_template('lab9/index.html', 
                         positions=BOX_POSITIONS,
                         remaining=remaining_boxes,
                         is_authenticated=is_authenticated)

@lab9.route('/lab9/open_box', methods=['POST'])
def open_box():
    data = request.get_json()
    box_id = data.get('box_id')
    
    # Проверяем, открывал ли пользователь уже 3 коробки
    if session['opened_count'] >= 3:
        return jsonify({
            "success": False,
            "message": "Вы уже открыли максимальное количество коробок (3)!"
        })
    
    # Проверяем, открывалась ли уже эта коробка (глобально)
    if box_id in opened_boxes:
        return jsonify({
            "success": False,
            "message": "Эта коробка уже пуста!"
        })
    
    # Проверяем, открывал ли пользователь эту коробку (в текущей сессии)
    if box_id in session['opened_by_user']:
        return jsonify({
            "success": False,
            "message": "Вы уже открывали эту коробку!"
        })
    
    # Находим данные коробки
    box_data = next((box for box in BOX_DATA if box["id"] == box_id), None)
    
    if box_data:
        # Проверяем, премиальная ли коробка
        if box_data["premium"] and not session.get('authenticated'):
            return jsonify({
                "success": False,
                "message": "Эта коробка только для авторизованных пользователей!"
            })
        
        # Отмечаем коробку как открытую (глобально)
        opened_boxes.add(box_id)
        
        # Обновляем данные сессии
        session['opened_count'] += 1
        session['opened_by_user'].append(box_id)
        session.modified = True
        
        # Обновляем количество оставшихся коробок
        remaining_boxes = 10 - len(opened_boxes)
        
        return jsonify({
            "success": True,
            "congratulation": box_data["congratulation"],
            "gift": box_data["gift"],
            "opened_count": session['opened_count'],
            "remaining_boxes": remaining_boxes
        })
    
    return jsonify({"success": False, "message": "Коробка не найдена!"})

@lab9.route('/lab9/reset', methods=['POST'])
def reset():
    # Для тестирования - сброс всех данных
    global opened_boxes
    opened_boxes.clear()
    session.clear()
    return jsonify({"success": True, "message": "Все коробки сброшены!"})

@lab9.route('/lab9/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    # Простая проверка логина и пароля
    if username == "Дед Мороз" and password == "2026":
        session['authenticated'] = True
        return jsonify({"success": True, "message": "Авторизация успешна!"})
    
    return jsonify({"success": False, "message": "Неверный логин или пароль!"})

@lab9.route('/lab9/logout', methods=['POST'])
def logout():
    session['authenticated'] = False
    return jsonify({"success": True, "message": "Вы вышли из системы!"})

@lab9.route('/lab9/check_auth')
def check_auth():
    return jsonify({"is_authenticated": session.get('authenticated', False)})