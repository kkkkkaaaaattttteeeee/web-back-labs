from flask import Blueprint, request, render_template, redirect, session
lab5 = Blueprint('lab5', __name__)


@lab5.route('/lab5/')
def lab():
    return render_template('lab5/lab5.html')

