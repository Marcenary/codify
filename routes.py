from routes_users import users_routes
from routes_tasks import tasks_routes
from blueprint.forum.routes_forum import forum_routes

def regist_routes(app, db, login):
    users_routes(app=app, db=db, login=login)
    tasks_bp = tasks_routes(app=app, db=db)
    forum_bp = forum_routes(app=app, db=db)
    
    app.register_blueprint(tasks_bp)
    app.register_blueprint(forum_bp)