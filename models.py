# Модуль моделей данных
from extensions import database as db
from datetime import datetime
from dataclasses import dataclass

from flask_login import UserMixin


@dataclass
class Lite:
	name:  	  str
	lvl: 	  int
	loged:    bool

@dataclass
class User:
	name:  	  str
	email: 	  str
	lvl: 	  int
	solved:	  int
	tasks_id: list
	# loged:    bool # <- in futured on/off-line user now
	date:     int

@dataclass
class Template:
	title:   str  = None
	info: 	 str  = None
	subinfo: str  = None
	user:    User = None
	tasks: 	 list = None

#UserMixin, 
class Clients(db.Model, UserMixin):
	__tablename__ = "Clients"

	id        = db.Column(db.Integer,  primary_key=True, unique=True)
	name      = db.Column(db.Text,     nullable=False)
	email     = db.Column(db.Text,     nullable=False)
	password  = db.Column(db.Text,     nullable=False, default="user")
	role      = db.Column(db.Text,     index=True)
	level     = db.Column(db.Integer,  default=1)
	solved    = db.Column(db.Integer,  default=0)
	tasks_id  = db.Column(db.Text,     default='[]')
	date      = db.Column(db.DateTime, default=datetime.utcnow)
	last_seen = db.Column(db.DateTime, default=datetime.utcnow)
	status    = db.Column(db.Integer,  default=0)

	def __repr__(self): return f"Clients: { self.name }"

	def is_admin(self):
		return self.role.lower() == "admin"

class Task(db.Model):
	__tablename__ = "Task"

	id        = db.Column(db.Integer, primary_key=True, unique=True)
	name      = db.Column(db.Text,    nullable=False)
	type      = db.Column(db.Integer, nullable=False)
	victorina = db.Column(db.Text,    nullable=False, default='[]')
	practic   = db.Column(db.Text,    nullable=False, default='[]')
	otvet     = db.Column(db.Text,    nullable=False) 
	task      = db.Column(db.Text,    nullable=False) 
	lang      = db.Column(db.Text,    nullable=False, default='["python", "javascript"]') # TODO: изменить на id из таблицы Lengs
	
	creator   = db.Column(db.Integer, db.ForeignKey('Clients.id'))

	def __repr__(self): return f"<Task { self.id }>"

class Lengs(db.Model):
	__tablename__ = "Lengs"

	id   = db.Column(db.Integer, primary_key=True, unique=True)
	name = db.Column(db.Text,    nullable=False)
	type = db.Column(db.Integer, nullable=False) # 0 - компилированный, 1 - интерпритируемый
	# icon = db.Column(db.Text,    nullable=False) # иконка(логотип) ЯП

	def __repr__(self): return f"Lengs: { self.name }"

# class Properties:
# 	__tablename__ = "Properties"

# 	id      = db.Column(db.Integer,  primary_key=True, unique=True)
# 	# TODO: Добавить все настройки позже - boolean(True-включиены, False-выключенны)
# 	creator = db.Column(db.Integer, db.ForeignKey('Clients.id'))

# class Forum(db.Model): # Threads
# 	__tablename__ = "Forum"

# 	id      = db.Column(db.Integer,  primary_key=True, unique=True)
# 	title   = db.Column(db.Text,     nullable=False)
# 	message = db.Column(db.Text,     nullable=False)
# 	date    = db.Column(db.DateTime, default=datetime.utcnow)
	
# 	lang        = db.Column(db.Text,    db.ForeignKey('Lengs.id')) # INFO: ЯП вопроса
# 	last_review = db.Column(db.Text,    db.ForeignKey('Thread.id'))
# 	creator     = db.Column(db.Integer, db.ForeignKey('Clients.id'), nullable=False) # INFO: Обязателен, тот кто создаёт

# 	def __repr__(self): return f"<Forum { self.id }>"

# class Thread(db.Model): # Related Reviews
# 	__tablename__ = "Thread"

# 	id      = db.Column(db.Integer,  primary_key=True, unique=True)
# 	message = db.Column(db.Text,     nullable=False)
# 	date    = db.Column(db.DateTime, default=datetime.utcnow)
	
# 	forum_id = db.Column(db.Integer, db.ForeignKey('Forum.id')) # INFO: К какому Треду относится отзыв
# 	creator  = db.Column(db.Integer, db.ForeignKey('Clients.id'))

# 	def __repr__(self): return f"<Thread { self.id }>"