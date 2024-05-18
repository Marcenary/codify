from route_api import api_routes
from routes_users import users_routes
from blueprint.tasks.routes_tasks import tasks_routes
from blueprint.forum.routes_forum import forum_routes

def regist_routes(app, db, login, mail, api):
    users_routes(app=app, db=db, login=login, mail=mail)
    tasks_bp = tasks_routes(app=app, db=db)
    forum_bp = forum_routes(app=app, db=db)
    api_routes(api=api, db=db)
    
    app.register_blueprint(tasks_bp)
    app.register_blueprint(forum_bp)