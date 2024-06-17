from models import Task
from flask import session, request, jsonify, json, abort
from flask_login import current_user
from flask_login.mixins import AnonymousUserMixin
from flask_restful import Resource, reqparse

from compile.languages.Interpreter import Python, JavaScript, TypeScript, Ruby, PHP

app = None
supports_lang = {
    "Python": Python,
    "JavaScript": JavaScript,
    "TypeScript": TypeScript,
    "Ruby": Ruby,
    "PHP": PHP
}
parser = reqparse.RequestParser()

class TasksResource(Resource):
    def get(self, types):
        _id = 0 if request.args.get("id") is None else int(request.args.get("id"))
        tasks = Task.query.all()

        if types == "tasks":
            out = []
            count = _id * 6
            for i in range(0, 6):
                index = count+i
                try:
                    out.append({
                        "id": tasks[index].id,
                        "name": tasks[index].name,
                        "task": tasks[index].task,
                        "lang": json.loads(tasks[index].lang),
                    })
                except IndexError: pass
        
        elif types == "task" and _id != "":
            out = Task.query.filter_by(id=_id).first()
            out = { i: out.__dict__[i] for i in out.__dict__ if i != '_sa_instance_state' }
            out["recipient"] = session.get('username')
        
        elif types == "total":
            return jsonify({ "total": tasks.count() })
        
        else: abort(404)

        return jsonify(out)

class CompileResource(Resource):
    def get(self):
        return { "data": f"Compiled code from { 'python' } lang." }
    
    def post(self):
        parser.add_argument('lang')
        parser.add_argument('name')
        parser.add_argument('code')
        data = parser.parse_args()

        if data["lang"] != None and data["lang"] in supports_lang:
            class_ = supports_lang[data["lang"]]
        
        try:
            user = "Anon"
            if not isinstance(current_user, AnonymousUserMixin):
                user = current_user.name

            caller = class_(data["name"], data["code"], user=user)
            if caller.build():
                app.logger.info("Command output: %s", True)
            out = caller.result
        except Exception as e:
            out = str(e)

        return {
            "data": f"Compiled code from { data['lang'] } lang.",
            "lang": data["lang"],
            "name": data["name"],
            "result": out
        }

def api_routes(api, db):
    '''Инициализация маршрутов API'''
    global app
    app = api.app
    api.add_resource(TasksResource,   "/api/v1/get/<types>")
    api.add_resource(CompileResource, "/api/v1/compile/")
    # api.add_resource(TasksResource,   "/api/<token>/v1/get/tasks")
    # api.add_resource(CompileResource, "/api/<token>/v1/compile/")