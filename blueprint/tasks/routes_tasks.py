from flask import Blueprint
from flask_login import login_required
from models import Clients, Task, Lengs, Template
from flask import (
	url_for, redirect,
	render_template,
	session, request,
	jsonify, json
)

def tasks_routes(app, db):
	'''Инициализация маршрутов заданий, использется Blueprint'''
	tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks") # template_folder="templates"

	@tasks_bp.get("/")
	@login_required
	def list_tasks():
		'''Страница заданий'''
		response = Template(title='Задания', info='Задания', subinfo='Выберите задания')
		return render_template('tasks.html', response=response) # tasks=tasks

	@tasks_bp.post("/add")
	@login_required
	def add_task():
		'''Страница добавления задания'''
		try:
			usr = Clients.query.filter(Clients.name == session.get('username')).first()
			
			task = Task(
				id=Task.query.count()+1,
				name=request.form.get("name"),
				type=0,
				creator=usr.id,
				practic=str(request.form.get("in").split(',')),
				otvet=str(request.form.get("out").split(',')),
				task=request.form.get("about"),
			)
			db.session.add(task)
			db.session.flush()
			db.session.commit()
			return redirect(url_for('list_tasks'))
		except Exception as e:
			db.session.rollback()
			app.logger.info('Ошибка добавления в БД: %s' % e)
			return jsonify(status="error")

	@tasks_bp.get("/task/<int:n>")
	@login_required
	def get_task(n: int):
		'''Страница выполнения задания'''
		name = session.get('username') or request.cookies.get('username')
		if name:
			task = Task.query.filter_by(id=n).first()
			task.lang = json.loads(task.lang)

			response = Template(title="Задание", info="", subinfo="")
			return render_template('task.html', response=response, task=task)
		return redirect(url_for('index'))

	@tasks_bp.post("/task")
	@login_required
	def post_task():
		'''Маршрут проверенного задания'''
		try:
			data = request.get_json()
			if data['status_task'] == 'success':
				client = Clients.query.filter(Clients.name == data['performed_task']).first()
				if data["id_task"] not in client.tasks_id:
					client.level += .5
					client.solved += 1
					client.tasks_id = json.loads(client.tasks_id)
					client.tasks_id.append(data['id_task'][0])
					client.tasks_id = json.dumps(client.tasks_id)
					db.session.commit()

					session['lvl'] = client.level
					app.logger.info('Данные БД обновлены')
				return redirect(url_for('profile'))
			return jsonify(status="Попробуйте ещё раз позже!")
		except Exception as e:
			db.session.rollback()
			app.logger.info('Ошибка добавления в БД: %s' % e)
			return jsonify(status="Попробуйте ещё раз позже!")

	@tasks_bp.route("/get/<n>")
	def api(n: str):
		'''API маршруты для облегчения обращения и получения нужной информации'''
		# if n == "tasks":
		# 	tasks, res = Task.query.all(), []
		# 	for task in tasks:
		# 		res.append({
		# 			"id": task.id,
		# 			"name": task.name,
		# 			"task": task.task,
		# 			"lang": json.loads(task.lang),
		# 		})
		# 	print(len(res))
		# 	return json.dumps(res)

		# if n == "task":
		# 	n = request.args.get('id')
		# 	task = Task.query.filter_by(id=n).first()
		# 	task = { i: task.__dict__[i] for i in task.__dict__ if i != '_sa_instance_state' }
		# 	task["recipient"] = session.get('username')
		# 	return task
			
		if n == "add_page":
			response = Template(title="Добавить задание", info="", subinfo="")
			return render_template('add_task.html', response=response)
		
		return "Uncorrect request!"

	@tasks_bp.post("/compile")
	def compile_task():
		'''Маршрут выполнения пользовательского кода'''
		import os

		out = ''
		jn = request.get_json()

		if 'os' not in jn or 'eval' not in jn:
			with open('compile/tmp.py', 'w') as f:
				f.write( jn['code'] + "\n\n\n" + jn['run'] )

		try:
			os.system('py compile/tmp.py')
			with open('compile/out.txt', 'r') as f: data = f.read().strip().split('\n')

			os.remove('compile/tmp.py')
			os.remove('compile/out.txt')
		except Exception as e: data = {'err': str(e)}
		return json.dumps(data)
	
	return tasks_bp