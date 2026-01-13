# models.py
from . import db
from flask_login import UserMixin

class users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(30), nullable=False, unique=True)
    password = db.Column(db.String(162), nullable=False)

class articles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    title = db.Column(db.String(50), nullable=False)
    article_text = db.Column(db.Text, nullable=False)
    is_favorite = db.Column(db.Boolean)
    is_public = db.Column(db.Boolean)
    likes = db.Column(db.Integer)
    
 # Конструктор (обязательно!)
    def __init__(self, login_id=None, title=None, article_text=None, 
                 is_favorite=False, is_public=False, likes=0):
        self.login_id = login_id
        self.title = title
        self.article_text = article_text
        self.is_favorite = is_favorite
        self.is_public = is_public
        self.likes = likes