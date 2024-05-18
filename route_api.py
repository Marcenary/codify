from flask_restful import Resource

class TasksResource(Resource):
    def get(self):
        return {"data": f"Return info about all tasks!"}

class TaskResource(Resource):
    def get(self, id: int):
        return {"data": f"Info about {id} task."}

class CompileResource(Resource): # как получить код?
    def get(self, lang: str):
        return {"data": f"Compiled code from {lang} lang."}

def api_routes(api, db):
    '''Инициализация маршрутов API'''
    api.add_resource(TasksResource,   "/api/v1/get/tasks")
    api.add_resource(TaskResource,    "/api/v1/get/task/<int:id>")
    api.add_resource(CompileResource, "/api/v1/compile/<lang>")