from app import app, database as db
from routes_users import *
# инициализация новых маршрутов
# from routes_tasks import *
# from blueprint.routes_forum import forum_bp

@app.get("/test")
def main():
	'''Тестовая функция для базы данных'''
	tmp = Clients.query.all()
	print(tmp)
	tmp = Task.query.all()
	print(tmp)
	return "If you see this message, thats Work!"

@app.get("/test/2")
def test2():
	return url_for('test')
