from flask import Blueprint
from flask_login import login_required, current_user
from models import Clients, Task, Complite, Lengs, Template
from flask import (
	url_for, redirect,
	render_template,
	session, request,
	jsonify, json
)

import os
import subprocess as subp

def tasks_routes(app, db):
	'''Инициализация маршрутов заданий, использется Blueprint'''
	tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks") # template_folder="templates"

	@tasks_bp.get("/")
	@login_required
	def list_tasks():
		'''Страница заданий'''
		lengs = Lengs.query.all()
		response = Template(title='Задания', info='Задания', subinfo='Выберите задания')
		return render_template('tasks.html', response=response, lengs=lengs) # tasks=tasks

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
			lengs = Lengs.query.all()
			task = Task.query.filter_by(id=n).first()
			
			task = { i: task.__dict__[i] for i in task.__dict__ if i != '_sa_instance_state' }
			task["lang"] = json.loads(task["lang"])
			
			tmp = []
			for i in task["lang"]:
				for el in lengs:
					if el.id == i:
						tmp.append(el.name)

			task["lang"] = tmp
			
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
				lang = Lengs.query.filter(Lengs.name==data["lang"]).first()
				task = Task.query.filter(Task.id==int(data["id_task"][0])).first()
				if data["id_task"] not in client.tasks_id or Complite.query.filter(Complite.lang==lang).count() == 0:
					client.level += .5
					client.solved += 1
					client.tasks_id = json.loads(client.tasks_id)
					client.tasks_id.append(data['id_task'][0])
					client.tasks_id = json.dumps(client.tasks_id)


					complited = Complite.query.filter(
						Complite.user == client.id,
						Complite.lang == lang.id,
						Complite.task == task.id
					)
					if complited.count() == 0:
						code = Complite(
							# id, # auto
							code=data["code"],
							# date, # auto
							task=task.id,
							user=client.id,
							lang=lang.id
						)
						db.session.add(code)
						db.session.flush()
					
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
		out, jn = '', ''
		try:
			jn = request.get_json()

			if 'os' not in jn['code'] or 'eval' not in jn['code']:
				with open(f'compile/languages/python/{ jn["name"] }.py', 'w') as f:
					f.write( jn['code'] )
			# else: raise ExceptionServer("Такой модуль не поддерживается")

			out = subp.run([ "python", f"compile/languages/python/{ jn['name'] }.py" ], capture_output=True)
			error = out.stderr
			if error != b'':
				result = error.decode()
				valid = "failed"
			else:
				with open('compile/languages/python/out.txt', 'r') as f: result = f.read().strip().split('\n')
				os.remove('compile/languages/python/out.txt')
				valid = "success"
		except Exception as e:
			print(e)
			result = 'Server error!'
			valid = "failed"
		finally:
			os.remove(f'compile/languages/python/{ jn["name"] }.py')

		return jsonify({
            "data": f"Compiled code from { jn['lang'] } lang.",
            "lang": jn["lang"],
            "name": jn["name"],
            "status": valid,
            "result": result
        })
	
	@tasks_bp.post("/compile/ruby")
	def compile_ruby():
		'''Маршрут выполнения пользовательского кода'''
		out, jn = '', ''
		try:
			jn = request.get_json()

			if 'os' not in jn['code'] or 'eval' not in jn['code']:
				with open(f'compile/languages/ruby/{ jn["name"] }.rb', 'w') as f:
					f.write( jn['code'] )

			out = subp.run([ "ruby", f"compile/languages/ruby/{ jn['name'] }.rb" ], capture_output=True)
			error = out.stderr
			
			if error != b'':
				result = error.decode()
				valid = "failed"
			else:
				with open('compile/languages/ruby/out.txt', 'r') as f: result = f.read().strip().split('\n')
				os.remove('compile/languages/ruby/out.txt')
				valid = "success"
		except Exception as e:
			result = 'Server error!'
			valid = "failed"
		finally:
			os.remove(f'compile/languages/ruby/{ jn["name"] }.rb')

		return jsonify({
            "data": f"Compiled code from { jn['lang'] } lang.",
            "lang": jn["lang"],
            "name": jn["name"],
            "status": valid,
            "result": result
        })
	
	@tasks_bp.post("/compile/js") # test
	def compile_js():
		'''Маршрут выполнения пользовательского кода'''
		out, jn = '', ''
		try:
			jn = request.get_json()

			if 'os' not in jn['code'] or 'eval' not in jn['code']:
				with open(f'compile/languages/javascript/{ jn["name"] }.js', 'w') as f:
					f.write( jn['code'] )

			out = subp.run([ "ruby", f"compile/languages/javascript/{ jn['name'] }.js" ], capture_output=True)
			error = out.stderr
			
			if error != b'':
				result = error.decode()
				valid = "failed"
			else:
				with open('compile/languages/javascript/out.txt', 'r') as f: result = f.read().strip().split('\n')
				os.remove('compile/languages/javascript/out.txt')
				valid = "success"
		except Exception as e:
			result = 'Server error!'
			valid = "failed"
		finally:
			os.remove(f'compile/languages/javascript/{ jn["name"] }.js')

		return jsonify({
            "data": f"Compiled code from { jn['lang'] } lang.",
            "lang": jn["lang"],
            "name": jn["name"],
            "status": valid,
            "result": result
        })
	
	@tasks_bp.post("/compile/php")
	def compile_php():
		'''Маршрут выполнения пользовательского кода'''
		out, jn = '', ''
		try:
			jn = request.get_json()

			if 'os' not in jn['code'] or 'eval' not in jn['code']:
				with open(f'compile/languages/php/{ jn["name"] }.php', 'w') as f:
					f.write( jn['code'].replace("include(\"./test.php\");", "function test($a=null, $b=null, $err=null) {\n\tfile_put_contents('compile/languages/php/out.txt', $err != null ? $err : json_encode($a == $b) . \"\n\", FILE_APPEND);\n}\n\n\n") )

			out = subp.run([ "php", f"compile/languages/php/{ jn['name'] }.php" ], capture_output=True)
			error = out.stderr
			
			if error != b'':
				result = error.decode()
				valid = "failed"
			else:
				with open('compile/languages/php/out.txt', 'r') as f: result = f.read().strip().split('\n')
				os.remove('compile/languages/php/out.txt')
				valid = "success"
		except Exception as e:
			result = 'Server error!'
			valid = "failed"
		finally:
			os.remove(f'compile/languages/php/{ jn["name"] }.php')

		return jsonify({
            "data": f"Compiled code from { jn['lang'] } lang.",
            "lang": jn["lang"],
            "name": jn["name"],
            "status": valid,
            "result": result
        })
	
	@tasks_bp.post("/compile/type")
	def compile_type():
		'''Маршрут выполнения пользовательского кода'''
		out, jn = '', ''
		try:
			jn = request.get_json()

			if 'os' not in jn['code'] or 'eval' not in jn['code']:
				with open(f'compile/languages/typescript/{ jn["name"] }.ts', 'w') as f:
					f.write( jn['code'] )

			out = subp.run([ "tsc", f"compile/languages/typescript/{ jn['name'] }.ts" ], capture_output=True)
			error = out.stdout
			
			if error != b'':
				result = error.decode()
				valid = "failed"
			else:
				out = subp.run([ "node", f"compile/languages/typescript/{ jn['name'] }.js" ], capture_output=True)
				error = out.stderr
			
				if error != b'':
					result = error.decode()
					valid = "failed"
				else:
					with open('compile/languages/typescript/out.txt', 'r') as f: result = f.read().strip().split('\n')
					os.remove('compile/languages/typescript/out.txt')
					valid = "success"
		except Exception as e:
			result = 'Server error!'
			valid = "failed"
		finally:
			os.remove(f'compile/languages/typescript/{ jn["name"] }.ts')
			os.remove(f'compile/languages/typescript/{ jn["name"] }.js')

		return jsonify({
            "data": f"Compiled code from { jn['lang'] } lang.",
            "lang": jn["lang"],
            "name": jn["name"],
            "status": valid,
            "result": result
        })
	
	return tasks_bp