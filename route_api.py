import subprocess as sp
from os import remove
from os.path import exists
from time import sleep

from models import Task
from flask import session, jsonify, json
from flask_restful import Resource, reqparse

from compile.languages.Interpreter import Python

app = None
supports_lang = {
    "Python": {
        "class": Python,
        "ext": "py",
        "program": "python3.10"
    },
    "JavaScript": {
        "class": "JavaScript",
        "ext": "js",
        "program": "node"
    },
    "TypeScript": {
        "class": "TypeScript",
        "ext": "ts",
        "program": "tode" # tode.sh - typescript tsc, nodejs
    },
    "Ruby": {
        "class": "Ruby",
        "ext": "rb",
        "program": "ruby"
    },
    "C": {
        "class": "CLang",
        "ext": "c",
        "program": "gcc"
    },
    "C++": {
        "class": "CPlusPlus",
        "ext": "cpp",
        "program": "g++"
    },
    "C#": {
        "class": "CSharp",
        "ext": "cs",
        "program": "cs" # or dotnet
    },
    "Java": {
        "class": "Java",
        "ext": "java",
        "program": "jythonc" # jythonc.sh - javac, java, jython
    },
}
parser = reqparse.RequestParser()

class TasksResource(Resource):
    def get(self):
        tasks, res = Task.query.all(), []
        for task in tasks:
            res.append({
				"id": task.id,
				"name": task.name,
				"task": task.task,
				"lang": json.loads(task.lang),
            })
        return jsonify(res)

class TaskResource(Resource):
    def get(self, id: int):
        task = Task.query.filter_by(id=id).first()
        task = { i: task.__dict__[i] for i in task.__dict__ if i != '_sa_instance_state' }
        task["recipient"] = session.get('username')
        return jsonify(task)

class CompileResource(Resource): # как получить код?
    def get(self):
        return { "data": f"Compiled code from { 'python' } lang." }
    
    def post(self):
        parser.add_argument('lang')
        parser.add_argument('code')
        data = parser.parse_args()

        if data["lang"] != None and data["lang"] in supports_lang:
            num    = 0
            lang   = supports_lang[data["lang"]]
            class_ = lang["class"]
            ext    = lang["ext"]
            prog   = lang["program"]

        search = "test{}.{}"
        name = search.format("", ext)
        while exists(name):
            num += 1
            name = search.format(num, ext)
        else:
            with open(search.format(num if num > 0 else "", ext), "w") as f:
                f.write(data["code"])

        # run = Python(name) # проверка кода и его сборка с возвратом результата
        process = sp.run([prog, name], capture_output=True)
        remove(name)

        out = process.stdout
        out = (out.decode() if out != b"" else process.stderr.decode()).strip().split("\n")[-1]

        app.logger.info("Command output: %s", out)
        return {
            "data": f"Compiled code from { data['lang'] } lang.",
            "lang": data["lang"],
            "code": data["code"],
            "result": out
        }

def api_routes(api, db):
    '''Инициализация маршрутов API'''
    global app
    app = api.app
    api.add_resource(TasksResource,   "/api/v1/get/tasks")
    api.add_resource(TaskResource,    "/api/v1/get/task/<int:id>") # ?
    api.add_resource(CompileResource, "/api/v1/compile/")
    # api.add_resource(TasksResource,   "/api/<token>/v1/get/tasks")
    # api.add_resource(TaskResource,    "/api/<token>/v1/get/task/<int:id>") # ?
    # api.add_resource(CompileResource, "/api/<token>/v1/compile/")