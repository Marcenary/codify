'''
Модуль моделей данных

Clients  # INFO: Пользователи сервиса
	* id
	* name  - Имя, ник, логин
	* email - почта
	* pwd_hash - хэш-пароль
	* role - роль пользователя (admin, user)
	* level - уровень, зависит от кол-во решенных заданий
	* solved - кол-во решенных заданий
	* tasks_id - идентификатор решенных заданий
	* date - дата регистрации
	* last_seen - дата последнего раза в сети
	* auth - 1 пользователь подтвердил почту
	* token - токен после подтверждения почты, для api обращения
	* status - в сети или нет

	+ last_time
	+ password
	+ verify_password

Task     # INFO: Задания пользователей
	* id
	* name - название
	* type - тип
	* victorina - тип первый
	* practic - тип второй
	* otvet - ответ(ы) на задания
	* task - задание
	* lang - ЯП поддерживаемые заданием

Complite # NEW INFO: Коды выполненных заданий
	* id
	* code - Пользовательский код
	* date - Дата выполнения
	* user - Автор выполненного кода
	* lang - ЯП выполненого задания

Lengs    # INFO: ЯП поддерж. сервисом, темы форума
	* id
	* name - Имя, название
	* type - тип (компилируемый, интерпретируемый)
	* icon - фото ЯП

Forum    # INFO: Вопросы форума на тему Lengs
	* id
	* name - Имя, название
	* size_review - последний ответ, thread
	* author - создатель вопроса
	* lang - ЯП, тема вопроса
	* last_review - последний ответ на вопрос

Thread   # INFO: Ответы на вопросы форума, конкретный вопрос
	* id
	* name - Имя, название
	* message - сообщение, текст
	* photo - возможное фото
	* remember - упоминание др. пользователя в сообщении
	* date - дата ответа
	* forum_id - отношение к теме, вопросу
	* author - автор вопроса
'''
from extensions import database as db
from datetime import datetime
from dataclasses import dataclass

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class Clients(db.Model, UserMixin):
	__tablename__ = "Clients"

	id        = db.Column(db.Integer,  primary_key=True, unique=True)
	name      = db.Column(db.Text,     nullable=False)
	email     = db.Column(db.Text,     nullable=False)
	pwd_hash  = db.Column(db.Text,     nullable=False)
	role      = db.Column(db.Text,     index=True, default="user")
	level     = db.Column(db.Integer,  default=1)
	solved    = db.Column(db.Integer,  default=0)
	tasks_id  = db.Column(db.Text,     default='[]')

	date      = db.Column(db.DateTime, default=datetime.now)
	last_seen = db.Column(db.DateTime, default=datetime.now)
	auth      = db.Column(db.Integer,  default=0)
	# token     = db.Column(db.Text)
	status    = db.Column(db.Integer,  default=0)

	def last_time(self):
		self.last_seen = datetime.now()

	def password(self, pwd):
		self.pwd_hash = generate_password_hash(pwd)

	def verify_password(self, pwd):
		return check_password_hash(self.pwd_hash, pwd)

	def __repr__(self): return f"Clients: { self.name }"

class Task(db.Model):
	__tablename__ = "Task"

	id        = db.Column(db.Integer, primary_key=True, unique=True)
	name      = db.Column(db.Text,    nullable=False)
	type      = db.Column(db.Integer, nullable=False)
	victorina = db.Column(db.Text,    nullable=False, default='[]')
	practic   = db.Column(db.Text,    nullable=False, default='[]')
	otvet     = db.Column(db.Text,    nullable=False) 
	task      = db.Column(db.Text,    nullable=False) 
	lang      = db.Column(db.Text,    nullable=False, default='[1, 2]')
	
	creator   = db.Column(db.Integer, db.ForeignKey('Clients.id'))

	def __repr__(self): return f"<Task { self.id }>"

class Complite(db.Model):
	__tablename__ = "Complite"

	id   = db.Column(db.Integer,  primary_key=True, unique=True)
	code = db.Column(db.Text,     nullable=False)
	date = db.Column(db.DateTime, default=datetime.now)
	user = db.Column(db.Integer,  db.ForeignKey('Clients.id'), nullable=False)
	task = db.Column(db.Integer,  db.ForeignKey('Task.id'), nullable=False)
	lang = db.Column(db.Integer,  db.ForeignKey('Lengs.id'))

class Lengs(db.Model):
	__tablename__ = "Lengs"

	id   = db.Column(db.Integer, primary_key=True, unique=True)
	name = db.Column(db.Text,    nullable=False)
	type = db.Column(db.Integer, nullable=False) # 0 - компилированный, 1 - интерпритируемый
	icon = db.Column(db.Text,    nullable=False, default="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADIAAAAyCAYAAAAeP4ixAAAACXBIWXMAAAsTAAALEwEAmpwYAAADTUlEQVR4nO2Za2jOURzHP8PckikvtKUke4HccimNF0JesHLL5d1yK9ckihdrKcWKZMiiSDEliZmGEHKbhlitKTOxlNs0l7nOHp06aj17nt/vnPPs2ajnW+fd//v9ne+5/M/v/A6kkEIKKQSgPzAFWAXsBy4Al4EK4D5wGygFDgMFQC6QyT+C4cB24BHQAkQC2lNgDzChMwzMAm4FdlxqVcACIC3ZBkYkyUB0uwuMSYYBM0KbgJ8dYCJi23dgWXua6AGc7EADkai2ub1MlHWiiYhtCc/Mcc+Av5Jk5BswKtTEOo9A54G5QJ5ish8w2S6XSk8zlUAXXxND7Cho4jXA9Fa8lcK3n2PEGQ1c9DCT52vEZV9cBfpE8bYI378T4s0GPjjErPY5Y3IcBMuBnjG4hQKn3uGMeu0Qu/UKEHFaEaoDMuJwS5TRdBnEH0r8Qy4msoHfipBJT+LhobIUXbBNif/WZXltdUgd4sH8UZoErpktF/S2+0nqxzBNpEoRWCxwByncXbhjRyIHZLZCNqOULvAXKnxzLrlivKK1WyIvVcjHlOAHFP5UDyNpQIOgdTaRjixSgtco/AH44aagZS5ycXFP6UiWwM1yWJa+OCrovZCI7wXiKyXoesWIyRR8sVfQa4xHSlfu3OYkl3BHMbIxwEihkoAGLY1iIeBgh8LD2AAjxZ4JqNMZkB84cn9P4q4BRsoEzTehM7I6Ds/cLz4q3H0BJtKUBPKBVFyTOmPuGbGQr/BMmxhgJEfRLJFG4ItAXBtnOX5SAj4JrFGdUHQ3SOTHAnFnDOOXklQ0mOSQgQ8NHYXrUd8WOJgwh1Z3TxOZlifpmsRWxBKB3GJzpYHAQQcTpq0IqBNUO+gu14SyEihER7drnnvD1HsbHXRr41yx26C0HUw02SuBC6YBNzy0Z/pstERMNAPzlD2Qay9OtZ7aRSS5uqj9pkcCp5SkVGvlyqUuJjJspcR3JmKd/qaq+DXBWS4HehEI8wd55hioQaisVCRgoMW+ZIXkaW3Ws1bOPKe8AzYHmngOzKCdYf4sZ2wSZ0bpJXAEGOfArfc0UG8flJx+sR2JNQ6dN5ekK8B8oBv/MObYp+oGu/Hr7LN1kS1e9+3sDqaQQgr8H/gDsEfUnVSjcZUAAAAASUVORK5CYII=")

	def __repr__(self): return f"{ self.name }"

class Forum(db.Model):
	__tablename__ = "Forum"

	id      = db.Column(db.Integer,  primary_key=True, unique=True)
	name    = db.Column(db.Text,     nullable=False)
	size_review = db.Column(db.Integer)
	author      = db.Column(db.Integer, db.ForeignKey('Clients.id'), nullable=False)
	lang        = db.Column(db.Text,    db.ForeignKey('Lengs.id'))
	last_review = db.Column(db.Integer, db.ForeignKey('Thread.id'))

	def __repr__(self): return f"Theme name: { self.id }"

class Thread(db.Model):
	__tablename__ = "Thread"

	id       = db.Column(db.Integer,  primary_key=True, unique=True)
	name     = db.Column(db.Text,     nullable=False)
	message  = db.Column(db.Text,     nullable=False)
	photo    = db.Column(db.Text,     nullable=False)
	remember = db.Column(db.Text,     nullable=False) # упомянуть пользователя
	date     = db.Column(db.DateTime, default=datetime.now)
	
	forum_id = db.Column(db.Integer, db.ForeignKey('Forum.id')) # INFO: К какому Треду относится отзыв
	author   = db.Column(db.Integer, db.ForeignKey('Clients.id'))

	def __repr__(self): return f"<Thread { self.id }>"

@dataclass
class User:
	name:  	  str
	email: 	  str
	lvl: 	  int
	solved:	  int
	tasks_id: list
	date:     int

@dataclass
class Template:
	title:   str  = None
	info: 	 str  = None
	subinfo: str  = None
	user:    Clients = None
	tasks: 	 list = None