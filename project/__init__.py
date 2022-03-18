from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from werkzeug.security import generate_password_hash

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'secretkey'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    with app.app_context():
        if bool(User.query.filter_by(teacher=2).first()) == False:
            print("init: no admin exists")
            email = "admin@gmail.com"
            name = "admin"
            password = "admin123"
            new_admin = User(User(email=email, name=name, password=generate_password_hash(
                password, method='sha256')))

            db.session.add(new_admin)
            db.session.commit()
        else:
            print("init: admin already exists")

    return app