'''Инициализация маршрутов форума, использется Blueprint'''
# from .importes import * # заменить на конкретные элементы
from flask import Blueprint

forum_bp = Blueprint("forum", __name__, template_folder="templates", url_prefix="/forum")

@forum_bp.route("/")
def forum_n():
    return f"You send nothing!"

@forum_bp.route("/<mess>")
def forum(mess: str):
    return f"You send {mess}"