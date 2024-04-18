from werkzeug.security import generate_password_hash, check_password_hash
from flask import url_for, redirect, render_template, session, request, flash, make_response, abort, jsonify, json
from db import app, db, Clients, Task, Template, User, Lite
# 15 defs, 5 classes

@app.route("/")
def index():
	response = Template(title='Авторизация', info="Пройдите регистрацию и начните тестирование ваши навыки", subinfo='Провертье свои знания', user=None)
	if 'username' in session or request.cookies.get('username'):
		return redirect(url_for('profile'))
	return render_template('index.html', response=response, nav_u=None)


@app.route("/sign", methods=['POST', 'GET'])
def signup():
	if request.method == 'POST':
		login = request.form.get('login') # name
		email = request.form.get('email')
		sump = generate_password_hash(request.form.get('password'))

		if Clients.query.filter(Clients.name == login).count() == 0:
			try:
				c = Clients(name=login, email=email, password=sump)
				db.session.add(c)
				db.session.flush()
				db.session.commit()
				if request.form.get('setcookies'):
					resp = make_response(redirect(url_for('profile')))
					resp.set_cookie('username', login)
					return resp
				session['username'] = login
				return redirect(url_for('profile'))
			except Exception as e:
				db.session.rollback()
				app.logger.info('Ошибка добавления в БД: %s' % e)
		else:
			flash('User is alredy exists', 'warning')

	return redirect(url_for('index'))


@app.route("/login", methods=['POST', 'GET'])
def login():
	if 'username' in session or request.cookies.get('username'):
		return redirect(url_for('profile'))

	if request.method == 'POST':		
		name = request.form.get('login')
		pasw = request.form.get('password')
		sql  = Clients.query.filter(Clients.name == name)

		if sql.count() != 0:
			if check_password_hash(sql[0].password, pasw):
				session['username'] = name
				session['lvl'] = sql[0].level
				session['loged'] = True
				if request.form.get('setcookies'):
					resp = make_response(redirect(url_for('profile')))
					resp.set_cookie('username', name)
					return resp
				return redirect(url_for('profile'))
			else:
				flash('Password: uncorrect password')
		else:
			flash('Login: this user not exists')

	return redirect(url_for('index'))


@app.route("/profile")
def profile():
	name = session.get('username') or request.cookies.get('username')
	if name:
		sql = Clients.query.filter(Clients.name == name)
		lite = Lite(name=name, lvl=sql[0].level, loged=True)
		user = User(
			name=name, email=sql[0].email,
			lvl=sql[0].level, solved=sql[0].solved,
			tasks_id=sql[0].tasks_id, date=sql[0].date)
		response = Template(title="Профиль", info='Профиль', subinfo=name, user=user)
		return render_template('profile.html', response=response, nav_u=lite)
	return redirect(url_for('index'))


@app.route("/profile/<int:n>")
@app.route("/profile/<n>")
def client(n):
	if type(n) is int:
		sql = Clients.query.filter(Clients.id == n)
	else: sql = Clients.query.filter(Clients.name == n)
	if sql.count() != 0:
		lite = Lite(name=session['username'], lvl=session['lvl'], loged=session['loged'])
		user = User(
			name=sql[0].name, email=sql[0].email,
			lvl=sql[0].level, solved=sql[0].solved,
			tasks_id=sql[0].tasks_id, date=sql[0].date,)
		response = Template(title=sql[0].name, info='Профиль', subinfo=sql[0].name, user=user)
		return render_template('profile.html', response=response, nav_u=lite)
	abort(404, description="This user not exists")


@app.errorhandler(404)
def resource_not_found(e):
    return str(e), 404


@app.route("/logout")
def logout():
	if'username' in session:
		session.pop('username', None)
	if request.cookies.get('username'):
		resp = make_response(redirect(url_for('index')))
		resp.delete_cookie('username')
		return resp
	return redirect(url_for('index'))


@app.route("/help")
def help():
	response = Template(title='Помощь', info="Помощь", subinfo="Эта страница ещё в разработке", user=None)
	return render_template('other.html', response=response, nav_u=None)


@app.route("/about")
def about():
	response = Template(title='Об Сервисе', info="Об Сервисе", subinfo="Эта страница ещё в разработке", user=None)
	return render_template('other.html', response=response, nav_u=None)


@app.get("/tasks")
@app.get("/tasks/<n>")
def list_tasks(n: str=""):
	if 'username' in session:
		lite = Lite(name=session['username'], lvl=session['lvl'], loged=session['loged'])
	else: lite = None

	response = Template(title='Задания', info='Задания', subinfo='Выберите задания')
	return render_template('tasks.html', response=response, nav_u=lite) # tasks=tasks


@app.post("/tasks/add")
def add_task():
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


@app.get("/task/<int:n>")
def get_task(n: int):
	name = session.get('username') or request.cookies.get('username')
	if name:
		task = Task.query.filter_by(id=n).first()
		task.lang = json.loads(task.lang)

		if 'username' in session:
			lite = Lite(name=session['username'], lvl=session['lvl'], loged=session['loged'])
		else: lite = None

		response = Template(title="Задание", info="", subinfo="")
		return render_template('task.html', response=response, nav_u=lite, task=task)
	return redirect(url_for('index'))


@app.post("/task")
def post_task():
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


@app.get("/get/<n>")
def api(n: str):
	if n == "tasks":
		tasks, res = Task.query.all(), []
		for task in tasks:
			res.append({
				"id": task.id,
				"name": task.name,
				"task": task.task,
				"lang": json.loads(task.lang),
			})
		return json.dumps(res)

	if n == "task":
		n = request.args.get('id')
		task = Task.query.filter_by(id=n).first()
		task = { i: task.__dict__[i] for i in task.__dict__ if i != '_sa_instance_state' }
		task["recipient"] = session.get('username')
		return task
	
	if n == "add_page":
		if 'username' in session:
			lite = Lite(name=session['username'], lvl=session['lvl'], loged=session['loged'])
		else: redirect(url_for('index'))

		response = Template(title="Добавить задание", info="", subinfo="")
		return render_template('add_task.html', response=response, nav_u=lite)


@app.post("/compile")
def compile_task():
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