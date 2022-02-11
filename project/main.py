from flask import Blueprint, render_template
from flask_login import current_user, login_required

from .models import User
from . import db

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/tutorial')
def tutorial():
    return render_template('tutorial.html')

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name, points=current_user.points) 

@main.route('/leaderboard')
@login_required
def leaderboard():
    #TODO - PROCESSING LEADERBOARD TABLE
    data = User.query.with_entities(User.name, User.points).order_by(User.points.desc()).limit(10).all()
    print(">>>>>>>>>>>>>>>")
    print(data[0])

    return render_template('leaderboard.html', items=data)

@main.route('/easy-questions')
@login_required
def easyQuestions():
    return render_template('easyQuestions.html')

@main.route('/hard-questions')
@login_required
def hardQuestions():
    return render_template('hardQuestions.html')