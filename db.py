from flask import Flask
from datetime import datetime
from dataclasses import dataclass
from flask_sqlalchemy import SQLAlchemy as SQL


app = Flask(__name__)
app.secret_key = b'192b9bdd22ab9ed4d12e236c78afcb9a393ec15f71bbf5dc987d54727823bcbf'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///TaskIfy.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQL(app)

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

class Clients(db.Model):
	__tablename__ = 'clients'
	id       = db.Column(db.Integer, primary_key=True, unique=True)
	name     = db.Column(db.Text, nullable=False)
	email    = db.Column(db.Text, nullable=False)
	password = db.Column(db.Text, nullable=False)
	level    = db.Column(db.Integer, default=1)
	solved   = db.Column(db.Integer, default=0)
	tasks_id = db.Column(db.Text, default='[]')
	date     = db.Column(db.DateTime, default=datetime.utcnow)

	def __repr__(self):
		return f"<Clients { self.name }>"

class Task(db.Model):
	__tablename__ = 'task'
	id        = db.Column(db.Integer, primary_key=True, unique=True)
	name      = db.Column(db.Text, nullable=False)
	type      = db.Column(db.Integer, nullable=False)
	creator   = db.Column(db.Integer, db.ForeignKey('clients.id'))
	victorina = db.Column(db.Text, nullable=False, default='[]')
	practic   = db.Column(db.Text, nullable=False, default='[]')
	otvet     = db.Column(db.Text, nullable=False)
	task      = db.Column(db.Text, nullable=False)
	lang      = db.Column(db.Text, nullable=False, default='["python", "javascript"]')

	def __repr__(self):
		return f"<Task { self.id }>"