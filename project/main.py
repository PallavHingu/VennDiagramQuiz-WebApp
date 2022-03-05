import random
from functools import wraps
from flask import Blueprint, jsonify, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required

from .models import User, Questions, History
from . import db

def teacher_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        print("current_user.teacher", current_user.teacher)
        if current_user.teacher == 1:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('main.index'))

    return wrap

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
    data = User.query.with_entities(User.name, User.points).filter_by(teacher = 0).order_by(User.points.desc()).limit(10).all()
    print(data[0])

    return render_template('leaderboard.html', items=data)

@main.route('/easy-questions')
@login_required
def easyQuestions():
    return render_template('easyQuestions.html')

@main.route('/add-hard-questions')
@login_required
@teacher_required
def addHardQuestions():
    return render_template('addHardQuestions.html')

@main.route('/hardQuestions', methods=['POST', 'GET'])
@login_required
def hardQuestions1():
    print("request", request.args)
    data = {}
    for key, value in request.form.items():
        data[key] = value

    print("data", data)


    all_done_qs = History.query.filter_by(user_id=current_user.id).all()
    all_done_qs_ids = []
    for qs in all_done_qs:
        all_done_qs_ids.append(qs.question_id)
    all_existing_qs = Questions.query.filter_by(difficulty=1).all()
    all_existing_qs_ids = []
    for qs in all_existing_qs:
        all_existing_qs_ids.append(qs.id)

    left_questions_ids = list(set(all_existing_qs_ids) - set(all_done_qs_ids))

    if len(left_questions_ids) == 0:
        return jsonify(["finished", "finished"])

    try:
        last_Q_num = data['question_number']
        this_Q_num = int(last_Q_num) + 1

        last_Q = Questions.query.filter_by(question=data['question_text']).first()
        last_Q_id = last_Q.id
        last_Q_answer = last_Q.answer

        left_questions_ids.remove(last_Q_id)
        print("left_questions_ids line 74", left_questions_ids)

        if last_Q_answer == data['input_answer']:
            # what happens when right answer
            print("CORRECT ANSWER")
            current_user.points += 100
            db.session.commit()
            is_correct = True
        else:
            print("WRONG ANSWER")
            is_correct = False

        # add completed question to history
        new_history = History(user_id=current_user.id, question_id=last_Q_id, correct=is_correct)
        print("saved to histroy")
        db.session.add(new_history)
        db.session.commit()

        if len(left_questions_ids) == 0:
            return jsonify(["finished", "finished"])

        this_Q_id = random.choice(left_questions_ids)
        print("this_Q_id", this_Q_id)
        this_Q = Questions.query.filter_by(id=this_Q_id).first()
        this_Q_text = this_Q.question

        
        

    except Exception as e:
        print("ERROR", e)
        last_Q_num = data['question_number']
        this_Q_num = int(last_Q_num) + 1 # Usually takes value 1
        print("left_questions_ids (for exception)", left_questions_ids)
        this_Q_id = random.choice(left_questions_ids) # Change to random I think
        this_Q = Questions.query.filter_by(id=this_Q_id).first()
        this_Q_text = this_Q.question


    
    all_done_qs = History.query.filter_by(user_id=current_user.id).all()
    all_done_qs_ids = []
    for qs in all_done_qs:
        all_done_qs_ids.append(qs.question_id)
    left_questions_ids = list(set(all_existing_qs_ids) - set(all_done_qs_ids))

    if len(left_questions_ids) == 0:
        return jsonify(["finished", "finished"])


    data_list = []

    data_list.append(this_Q_num)
    data_list.append(this_Q_text)

    return jsonify(data_list)
    

@main.route('/completed-all-questions')
@login_required
def completedAllQuestions():
    return render_template('allHardQuestionsCompletedOnce.html')

@main.route('/hard-questions')
@login_required
def hardQuestions():
    return render_template('hardQuestions.html')

# @main.route('/hard-questions/<question_text>', methods=["POST"])
# @login_required
# def hardQuestions_check(question_text):
#     question = Questions.query.filter_by(question=question_text).first()
#     question_answer = question.answer
#     user_answer = request.form.get('answer')
#     print("USER", user_answer)
#     print("ACTUAL", question_answer)

#     if user_answer == question_answer:
#         print(">>>>>>>>>>CORRECT Answer!")
#         return "CHECKED"
    
#     print(">>>>>>>>>>WRONG Answer!")
#     return "CHECKED"