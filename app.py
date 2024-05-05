from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy as SQL

from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView

from blueprint.forum.routes_forum import forum_bp

from extensions import database

# Отредактировать прошлую БД под новую, что бы не заполнять данные!!!

app = Flask(__name__)
admin = Admin(name="Codify", template_mode="bootstrap4")
migrate = Migrate()

def create_app(debug=True) -> None:
    '''
    Инициализирующая функция
    Не принимает аргументов, возвращает None
    '''

    app.secret_key = b'192b9bdd22ab9ed4d12e236c78afcb9a393ec15f71bbf5dc987d54727823bcbf'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///TaskIfy.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    admin.init_app(app=app)
    database.init_app(app=app)
    migrate.init_app(app=app, db=database)

    from models import Clients, Task, Lengs, GoMain
    
    app.register_blueprint(forum_bp)
    admin.add_view(ModelView(Clients, database.session, name="Пользователи"))
    admin.add_view(ModelView(Task,    database.session, name="Задания"))
    admin.add_view(ModelView(Lengs, database.session, name="Языки Программирования"))
    # admin.add_view(ModelView(Forum, database.session, name="Форум?"))
    admin.add_view(GoMain(name="На главную"))

    return app

if __name__ == "__main__":
    app = create_app()