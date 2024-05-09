from flask import abort, redirect, url_for
from flask_admin import BaseView, expose
from flask_admin.contrib.sqla import ModelView

from flask_login import current_user

class PanelView(BaseView): # In future Settings
    def is_accessible(self):
        if current_user.is_authenticated:
            return current_user.is_authenticated
        # return abort(404)
        
    def not_auth(self):
        return "403!"

    @expose('/')
    def main_page(self: BaseView):
        # return self.render("admin/back.html")
        return redirect(url_for("profile"))

class GuardModelView(ModelView):
    def is_accessible(self):
        if current_user.role == "admin":
            return current_user.is_authenticated

def regist_admin_panel(admin, db, **kwargs):
    from models import Clients, Task, Lengs
    
    admin.add_view(GuardModelView(Clients, db.session, name="Пользователи"))
    admin.add_view(GuardModelView(Task,    db.session, name="Задания"))
    admin.add_view(GuardModelView(Lengs,   db.session, name="Языки Программирования"))
    # admin.add_view(ModelView(Forum, database.session, name="Форум?"))
    admin.add_view(PanelView(name="На главную"))