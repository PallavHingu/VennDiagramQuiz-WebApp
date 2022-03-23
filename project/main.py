from cmath import log
from crypt import methods
import random
from functools import wraps
from urllib import response
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
        elif current_user.teacher == 2:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('main.index'))

    return wrap

def admin_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        print("current_user.teacher", current_user.teacher)
        if current_user.teacher == 2:
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

@main.route('/home')
@login_required
def home():
    if current_user.teacher == 0:
        return render_template('home.html', name=current_user.name, points=current_user.points) 
    elif current_user.teacher == 1:
        return render_template('teacherHome.html', name=current_user.name)
    elif current_user.teacher == 2:
        return render_template('adminHome.html', name=current_user.name)
    else:
        return ""

@main.route('/leaderboard')
@login_required
def leaderboard():
    #TODO - PROCESSING LEADERBOARD TABLE
    data = User.query.with_entities(User.name, User.points).filter_by(teacher = 0).order_by(User.points.desc()).limit(10).all()
    print(data[0])

    return render_template('leaderboard.html', items=data)

@main.route('/add-hard-questions')
@login_required
@teacher_required
def addHardQuestions():
    return render_template('addHardQuestions.html')

@main.route('/hardQuestions', methods=['POST', 'GET'])
@login_required
def hardQuestions1():
    # this is the API function used for AJAX javascript
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

    if int(data["question_number"]) >= 10:
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
            current_user.points += 20
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
            return jsonify(["finished", "finished", is_correct, last_Q_answer])

        this_Q_id = random.choice(left_questions_ids)
        print("this_Q_id", this_Q_id)
        this_Q = Questions.query.filter_by(id=this_Q_id).first()
        this_Q_text = this_Q.question

        
    except Exception as e:
        print("ERROR ", e)
        last_Q_num = data['question_number']
        this_Q_num = int(last_Q_num) + 1 # Usually takes value 1
        print("left_questions_ids (for exception)", left_questions_ids)
        this_Q_id = random.choice(left_questions_ids)
        this_Q = Questions.query.filter_by(id=this_Q_id).first()
        this_Q_text = this_Q.question
        is_correct = None
        last_Q_answer = ""


    
    all_done_qs = History.query.filter_by(user_id=current_user.id).all()
    all_done_qs_ids = []
    for qs in all_done_qs:
        all_done_qs_ids.append(qs.question_id)
    left_questions_ids = list(set(all_existing_qs_ids) - set(all_done_qs_ids))

    if len(left_questions_ids) == 0:
        return jsonify(["finished", "finished", is_correct, last_Q_answer])


    data_list = []

    data_list.append(this_Q_num)
    data_list.append(this_Q_text)
    data_list.append(is_correct)
    data_list.append(last_Q_answer)

    return jsonify(data_list)


@main.route('/hard-questions')
@login_required
def hardQuestions():
    return render_template('hardQuestions.html')


@main.route('/easy-questions')
@login_required
def easyQuestions():
    return render_template('easyQuestions.html')

@main.route("/easyQuestions", methods=["POST", "GET"])
@login_required
def easyQuestions1():
    # this is the API function used for AJAX javascript
    print("request", request.args)
    data = {}
    for key, value in request.form.items():
        data[key] = value

    print("data", data)

    all_done_qs = History.query.filter_by(user_id=current_user.id).all()
    all_done_qs_ids = []
    for qs in all_done_qs:
        all_done_qs_ids.append(qs.question_id)
    all_existing_qs = Questions.query.filter_by(difficulty=0).all() # get all easy questions with dif=0
    all_existing_qs_ids = []
    for qs in all_existing_qs:
        all_existing_qs_ids.append(qs.id)
    
    left_questions_ids = list(set(all_existing_qs_ids) - set(all_done_qs_ids))

    if len(left_questions_ids) == 0:
        return jsonify(["finished", "finished"])
    
    if int(data["question_number"]) >= 10:
        return jsonify(["finished", "finished"])

    try:
        last_Q_num = data['question_number']
        this_Q_num = int(last_Q_num) + 1

        last_Q = Questions.query.filter_by(question=data['question_text']).first()
        last_Q_id = last_Q.id
        last_Q_answer = last_Q.answer

        left_questions_ids.remove(last_Q_id)

        print("EASY INPUTED ANSWER: " + data['input_answer'])

        if last_Q_answer == data['input_answer']:
            # what happens when right answer
            print("CORRECT ANSWER")
            current_user.points += 10
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
            return jsonify(["finished", "finished", is_correct, last_Q_answer])

        this_Q_id = random.choice(left_questions_ids)
        print("this_Q_id", this_Q_id)
        this_Q = Questions.query.filter_by(id=this_Q_id).first()
        this_Q_text = this_Q.question

    except Exception as e:
        print("ERROR ", e)
        last_Q_num = data['question_number']
        this_Q_num = int(last_Q_num) + 1 # Usually takes value 1
        print("left_questions_ids (for exception)", left_questions_ids)
        this_Q_id = random.choice(left_questions_ids)
        this_Q = Questions.query.filter_by(id=this_Q_id).first()
        this_Q_text = this_Q.question
        is_correct = None
        last_Q_answer = ""

    all_done_qs = History.query.filter_by(user_id=current_user.id).all()
    all_done_qs_ids = []
    for qs in all_done_qs:
        all_done_qs_ids.append(qs.question_id)
    left_questions_ids = list(set(all_existing_qs_ids) - set(all_done_qs_ids))

    if len(left_questions_ids) == 0:
        return jsonify(["finished", "finished", is_correct, last_Q_answer])

    data_list = []

    data_list.append(this_Q_num)
    data_list.append(this_Q_text)
    data_list.append(is_correct)
    data_list.append(last_Q_answer)

    return jsonify(data_list)


@main.route("/addPoints", methods=["POST"])
@login_required
def addPoints():
    data = {}
    for key, value in request.form.items():
        data[key] = value

    try:
        points = data["points"]
        print(">>> before points", current_user.points)
        current_user.points = points
        db.session.commit()
        print(">>> after points", current_user.points)
        return "added points"
    except Exception as e:
        print("error: ", e)
        return e
    

@main.route('/add-easy-questions')
@login_required
@teacher_required
def addEasyQuestions():
    return render_template('addEasyQuestions.html')

@main.route("/addQs", methods=["POST", "GET"])
@login_required
@teacher_required
def addQuestion():
    data = {}
    for key, value in request.form.items():
        data[key] = value

    print("received ADD QS: ", data["question_text"], data["input_answer"], data["difficulty"])

    try:
        # add new qs
        if (len(data["question_text"]) > 0):
            new_q = Questions(question = data["question_text"], answer=data["input_answer"], difficulty=data["difficulty"])
            db.session.add(new_q)
            db.session.commit()
            return "Q Added"
        else:
            return "Q Blank"
    except Exception as e:
        print("ERROR: ", e)
        return "Not added"


@main.route("/updQs", methods=["POST", "GET"])
@login_required
@teacher_required
def updateQuestion():
    data = {}
    for key, value in request.form.items():
        data[key] = value

    print("received update QS: ", data["question_id"], data["question_text"], data["input_answer"], data["difficulty"])

    try:
        # add new qs
        if (len(data["question_text"]) > 0):
            new_q = Questions(id=data["question_id"], question = data["question_text"], answer=data["input_answer"], difficulty=data["difficulty"])
            old_q = Questions.query.filter_by(id=data["question_id"]).first()
            old_q.question = new_q.question
            old_q.answer = new_q.answer
            db.session.commit()
            return "Q Added"
        else:
            return "Q Blank"
    except Exception as e:
        print("ERROR: ", e)
        return "Not added"

   
@main.route("/allQuestions")
@login_required
@teacher_required
def allQuestions():
    questions = Questions.query.all()
    print("All questions show: ", questions)
    return render_template("manageAllQuestions.html", questions=questions)


@main.route("/viewQuestion")
@login_required
@teacher_required
def viewQuestion():
    try: 
        id = request.args.get("id")
        question = Questions.query.filter_by(id=id).first()
    except Exception as e:
        print("error:", e)
        e = str(e)
        return "error: " + e

    return render_template("viewQuestion.html", question=question)


@main.route("/editQuestion")
@login_required
@teacher_required
def editQuestion():
    try: 
        id = request.args.get("id")
        question = Questions.query.filter_by(id=id).first()
    except Exception as e:
        print("error:", e)
        e = str(e)
        return "error: " + e

    return render_template("editQuestion.html", question=question)

@main.route('/delQ', methods=["POST"])
@login_required
@teacher_required
def deleteQuestion1():
    try:
        id = request.args.get("id")
        Questions.query.filter_by(id=id).delete()
        db.session.commit()
    except Exception as e:
        print("error", e)
        e = str(e)
        return "error: " + e 
    return redirect(url_for("main.allQuestions"))

@main.route("/historyQs")
@login_required
@teacher_required
def historyQuestions():
    history = History.query.all()
    users = User.query.all()
    questions = Questions.query.all()
    print("All QS history: ", history)
    print("All Users: ", users)
    print("All Questions: ", questions)
    return render_template("historyOfQuestions.html", history=history, users=users, questions=questions)

@main.route("/manageUsers")
@login_required
@admin_required
def manageUsers():
    users = User.query.filter(User.id != current_user.id)
    return render_template("manageUsers.html", users=users)

@main.route("/deleteUser/<userId>", methods=["POST"])
@login_required
@admin_required
def deleteUser(userId):
    if userId == current_user.id:
        return "That's YOU!!!!"
    else:
        print("remove user with id: ", userId)
        user = User.query.filter_by(id=userId).first()
        db.session.delete(user)
        db.session.commit()
        return redirect(url_for("main.manageUsers"))

@main.route("/editUser/<userId>", methods=["GET"])
@login_required
@admin_required
def editUser(userId):
    if userId == current_user.id:
        return "That's YOU!!!"
    else:
        user = User.query.filter_by(id=userId).first()
        return render_template("editUser.html", user=user)


@main.route("/editUser", methods=["POST"])
@login_required
@admin_required
def editUserPost():

    data = {}
    for key, value in request.form.items():
        data[key] = value

    print("received update User: ", data["user_id"], data["user_email"], data["user_name"], data["user_teacher"], data["user_points"])

    userId = data["user_id"]
    if userId == current_user.id:
        return "That's YOU!!!"
    email = data["user_email"]
    name = data["user_name"]
    try:
        teacher = int(data["user_teacher"])
    except Exception as e:
        print("Error: ", e)
        e = str(e)
        return "Error: " + e
    try:
        points = int(data["user_points"])
    except Exception as e:
        print("Error: ", e)
        e = str(e)
        return "Error: " + e
    
    user = User.query.filter_by(id=int(userId)).first()
    
    user.email = email
    user.name = name
    if teacher > 2: # user.teacher has to be 0, 1 or 2
        teacher = 2
    if teacher < 0:
        teacher = 0
    user.teacher = teacher
    if user.teacher > 0: # teacher and admin have points = 0 
        points = 0 
    user.points = points
    
    db.session.commit()

    return "User Updated"
