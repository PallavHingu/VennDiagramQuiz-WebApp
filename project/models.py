from . import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    points = db.Column(db.Integer, default=0)
    teacher = db.Column(db.Integer, default=0)

class Questions(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    question = db.Column(db.String(1000), nullable = False)
    answer = db.Column(db.String(1000), nullable = False)
    difficulty = db.Column(db.Integer, nullable = False)

class History(db.Model):
    id = db.Column(db.Integer, primary_key = True) 
    user_id  = db.Column(db.Integer)
    question_id = db.Column(db.Integer)
    correct = db.Column(db.Integer)

