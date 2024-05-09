from flask import Blueprint
from models import Clients, Template, User
from flask import (
	# url_for, redirect,
	render_template,
	# session, request,
	# flash, make_response,
	# abort
)

def forum_routes(app, db):
    '''Инициализация маршрутов форума, использется Blueprint'''
    forum_bp = Blueprint("forum", __name__, template_folder="blueprint/forum/templates", url_prefix="/forum")

    @forum_bp.route("/")
    def forum_n():
        response = Template(title='Форум', info="Форум", subinfo="Эта страница ещё в разработке")
        return render_template('forum/index.html', response=response)

    @forum_bp.route("/<mess>")
    def forum(mess: str):
        return f"You send {mess}"
    
    return forum_bp