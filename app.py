from flask import Flask
from flask_admin import Admin
from flask_login import LoginManager
from flask_restful import Api
from flask_gravatar import Gravatar
from flask_migrate import Migrate
from flask_mail import Mail

from routes_admin import regist_admin_panel
from routes import regist_routes
from extensions import database as db
# Отредактировать прошлую БД под новую, что бы не заполнять данные!!!

def create_app() -> None:
    '''
    Инициализирующая функция
    Не принимает аргументов, возвращает None
    '''

    app = Flask(__name__)
    app.secret_key = b'192b9bdd22ab9ed4d12e236c78afcb9a393ec15f71bbf5dc987d54727823bcbf'
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///TaskIfy.db'
    # app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config.from_pyfile('config.cfg')

    # admin.init_app(app=app)
    # migrate.init_app(app=app, db=database)
    db.init_app(app=app)
    admin   = Admin(app=app, name="Codify", template_mode="bootstrap4")
    login   = LoginManager(app=app)
    api     = Api(app=app)
    avatar  = Gravatar(app=app) # modified module flask_gravatar, copy code
    migrate = Migrate(app=app, db=db)
    mail    = Mail(app=app)

    regist_routes(app=app, db=db, login=login, mail=mail, api=api)
    regist_admin_panel(admin=admin, db=db)

    return app

if __name__ == "__main__":
    app = create_app()