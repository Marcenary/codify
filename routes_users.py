from werkzeug.security import generate_password_hash, check_password_hash
from models import Clients, Template, User

from flask_login import login_user, logout_user, current_user, login_required
from flask import (
	url_for, redirect,
	render_template,
	session, request,
	flash, make_response,
	abort
)

def users_routes(app, db, login):
    '''Инициализация пользовательских маршрутов'''
    @login.user_loader
    def load_user(uid): return Clients.query.get(uid)

    @login.unauthorized_handler
    def unauthorized_handler():
        # временно
        response = Template(title='Не зарегистрированное обращение', info="Не зарегистрированное обращение!", subinfo='Зарегистрируйтесь для обращения!', user=None)
        return render_template("index2.html", nav_u=None)

    @app.errorhandler(404)
    def resource_not_found(e):
        '''Страница 404'''
        return f"<html><head><title>Ошибка 404</title></head><body><h1 style='margin: auto; width: 75vw; display: flex; justify-content: center;'>{ str(e) }</h1></body></html>"
    
    @app.route("/")
    def index():
        '''Главная страница'''
        response = Template(title='Авторизация', info="Пройдите регистрацию и начните тестирование ваши навыки", subinfo='Провертье свои знания', user=None)
        if 'username' in session or request.cookies.get('username'):
            return redirect(url_for('profile'))
        # временно
        return render_template('index.html', response=response, nav_u=None)

    @app.route("/login", methods=["GET", "POST"])
    def login():
        '''Маршрут авторизации'''
        if 'username' in session or request.cookies.get('username'):
            return redirect(url_for('profile'))

        if request.method == 'POST':		
            name = request.form.get('login')
            pasw = request.form.get('password')
            sql  = Clients.query.filter(Clients.name == name)

            if sql.count() != 0:
                usr = sql.first() # 
                if check_password_hash(usr.password, pasw):
                    login_user(usr)
                    session['username'] = name
                    session['lvl'] = sql[0].level
                    session['loged'] = True

                    if request.form.get('setcookies'):
                        resp = make_response(redirect(url_for('profile')))
                        resp.set_cookie('username', name)
                        return resp
                    
                    return redirect(url_for('profile'))
                else:
                    flash('Password: uncorrect password')
            else:
                flash('Login: this user not exists')
                
        return redirect(url_for('index'))

    @app.route("/sign", methods=["GET", "POST"])
    def signup():
        '''Маршрут регистрации'''
        if 'username' in session or request.cookies.get('username'):
            return redirect(url_for('profile'))
        
        if request.method == "POST":
            uname = request.form.get("login")
            email = request.form.get("email")
            sump = generate_password_hash(request.form.get('password'))

            if Clients.query.filter(Clients.name == login).count() == 0:
                try:
                    c = Clients(name=login, email=email, password=sump)
                    db.session.add(c)
                    db.session.flush()
                    db.session.commit()
                    login_user(name)

                    if request.form.get('setcookies'):
                        resp = make_response(redirect(url_for('profile')))
                        resp.set_cookie('username', login)
                        return resp
                    session['username'] = login

                    return redirect(url_for('profile'))
                except Exception as e:
                    db.session.rollback()
                    app.logger.info('Ошибка добавления в БД: %s' % e)
            else:
                flash('User is alredy exists', 'warning')
            
        return redirect(url_for('index'))

    @app.route("/logout")
    def logout():
        '''Маршрут деавторизации'''
        current_user.last_time()
        logout_user()

        if 'username' in session:
            session.pop('username', None)
        
        if request.cookies.get('username'):
            resp = make_response(redirect(url_for('index')))
            resp.delete_cookie('username')
            return resp
        
        return redirect(url_for('index'))

    @app.route("/setcookie")
    def setcookie():
        return "Success"
    
    @app.route("/deletecookie")
    def deletecookie():
        return "Success"

    @app.route("/profile")
    @login_required
    def profile():
        '''Страница профиля'''
        # name = session.get('username') or request.cookies.get('username')
        # if name:
        response = Template(title="Профиль", info='Профиль')
        return render_template('profile.html', response=response)

    @app.route("/profile/<int:n>")
    @app.route("/profile/<n>")
    def client(n):
        '''Страницы др. пользователей'''
        if type(n) is int:
            sql = Clients.query.filter(Clients.id == n)
        else: sql = Clients.query.filter(Clients.name == n)
        
        if sql.count() != 0:
            user = sql.first()
            response = Template(title=f'Профиль { user.name }', info='Профиль', subinfo=user.name, user=user)
            return render_template('profile_friend.html', response=response)
        abort(404, description="This user not exists")

    @app.route("/help")
    def help():
        '''Страница помощи'''
        response = Template(title='Помощь', info="Помощь", subinfo="Эта страница ещё в разработке")
        return render_template('other.html', response=response)

    @app.route("/about")
    def about():
        '''Информационная страница'''
        response = Template(title='Об Сервисе', info="Об Сервисе", subinfo="Эта страница ещё в разработке")
        return render_template('other.html', response=response)