from flask import Blueprint, request, render_template
lab4 = Blueprint('lab4', __name__)


@lab4.route('/lab2/')
def lab():
    return render_template('lab4/lab4.html')