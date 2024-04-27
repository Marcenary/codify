# 1) Сначала запустить код в таком виде
# 2) После команда flask db init для flask migrate
# Должна появиться папка instance после 1 или 2 действия, в ней должна быть база данных
# ...
# Инициализировать базу данных методом db.init_app(app) после всех методов объекта app(Flask)
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy as SQL
from flask_admin import Admin
from flask_admin.contrib import ModelView

# Временно

# 

app = Flask(__name__)
app.secret_key = b'192b9bdd22ab9ed4d12e236c78afcb9a393ec15f71bbf5dc987d54727823bcbf'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///TaskIfy.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQL(app)
admin = Admin(app)
migrate = Migrate(app, db)

# not exsists in app.py
# admin.add_wiew(ModelView(Clients, db.session))

if __name__ == "__main__": # or def create_app()
    try:
        db.init_app(app) # if db = SQL()
        admin.init_app(app) # if admin = Admin()
        # without try\except
    except RuntimeError:
        pass
