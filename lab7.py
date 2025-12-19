from flask import Blueprint, request, render_template, jsonify

lab7 = Blueprint('lab7', __name__)

@lab7.route('/lab7/')
def main():
    return render_template('lab7/index.html')

films = [
    {
        "title": "Interstellar",
        "title_ru": "Интерстеллар",
        "year": 2014,
        "description": "Когда засуха, пыльные бури и вымирание растений приводят человечество к продовольственному кризису, коллектив исследователей и учёных отправляется сквозь червоточину (которая предположительно соединяет области пространства времени через большое расстояние) в путешествие, чтобы превзойти прежние ограничения для космических путешествий человека и найти планету с подходящими для человечества условиями."
    },
    {
        "title": "The Shawshank Redemption",
        "title_ru": "Побег из Шоушенка",
        "year": 1994,
        "description": "Бухгалтер Энди Дюфрейн обвинён в убийстве собственной жены и её любовника. Оказавшись в тюрьме под названием Шоушенк, он сталкивается с жестокостью и беззаконным, царящими по обе стороны решётки. Каждый, кто попадает в эти стены, становится их рабом до конца жизни. Но Энди, обладающий жилым умом и доброй душой, находит подход как к заключённым, так и к охранникам, добиваясь их особого к себе расположения."
    },
    {
        "title": "The Green Mile",
        "title_ru": "Зеленая миля",
        "year": 1999,
        "description": "Пол Эджкомб — начальник блока смертников в тюрьме «Холодная гора». Каждый из узников которого однажды проходит последний путь по зловещей коридорной плитке, отмеченной зелёным линолеумом, в сторону электрического стула. Вскоре к нему поступает необычный заключённый — гигант Джон Коффи, осуждённый за страшное преступление, но обладающий удивительными целительными способностями и детской душой. Эта встреча навсегда изменит жизнь Пола и заставит его задуматься о чудесах, справедливости и смысле наказания."
    }
]

def validate_film_data(film):
    """Валидация данных фильма"""
    errors = {}
    
    # Проверка описания
    if not film.get('description') or film['description'].strip() == '':
        errors['description'] = 'Заполните описание'
    
    # Проверка русского названия
    if not film.get('title_ru') or film['title_ru'].strip() == '':
        errors['title_ru'] = 'Введите название на русском'
    
    # Проверка года
    if not film.get('year'):
        errors['year'] = 'Введите год выпуска'
    else:
        try:
            year = int(film['year'])
            if year < 1888 or year > 2024:  # 1888 - год первого фильма
                errors['year'] = 'Введите корректный год (1888-2024)'
        except ValueError:
            errors['year'] = 'Год должен быть числом'
    
    # Если оригинальное название пустое, но русское задано, используем русское
    if (not film.get('title') or film['title'].strip() == '') and film.get('title_ru'):
        film['title'] = film['title_ru']
    
    return errors, film

@lab7.route('/lab7/rest-api/films/', methods=['GET'])
def get_films():
    return jsonify(films)

@lab7.route('/lab7/rest-api/films/<int:id>', methods=['GET'])
def get_film(id):
    if id < 0 or id >= len(films):
        return jsonify({"error": "Film not found"}), 404
    return jsonify(films[id])

@lab7.route('/lab7/rest-api/films/<int:id>', methods=['DELETE'])
def del_film(id):
    if id < 0 or id >= len(films):
        return jsonify({"error": "Film not found"}), 404
    del films[id]
    return '', 204

@lab7.route('/lab7/rest-api/films/<int:id>', methods=['PUT'])
def put_film(id):
    if id < 0 or id >= len(films):
        return jsonify({"error": "Film not found"}), 404
    
    film = request.get_json()
    
    # Валидация данных
    errors, validated_film = validate_film_data(film)
    if errors:
        return jsonify(errors), 400
    
    films[id] = validated_film
    return jsonify(films[id]), 200

@lab7.route('/lab7/rest-api/films/', methods=['POST'])
def add_film():
    film = request.get_json()
    
    # Валидация данных
    errors, validated_film = validate_film_data(film)
    if errors:
        return jsonify(errors), 400
    
    films.append(validated_film)
    return jsonify({"id": len(films) - 1}), 201