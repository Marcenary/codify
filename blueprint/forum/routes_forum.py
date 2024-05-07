from flask import Blueprint
# from .importes import * # заменить на конкретные элементы

def forum_routes(app, db):
    '''Инициализация маршрутов форума, использется Blueprint'''
    forum_bp = Blueprint("forum", __name__, template_folder="templates", url_prefix="/forum")

    @forum_bp.route("/")
    def forum_n():
        return f"You send nothing!"

    @forum_bp.route("/<mess>")
    def forum(mess: str):
        return f"You send {mess}"
    
    return forum_bp