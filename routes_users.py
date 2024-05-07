from werkzeug.security import generate_password_hash, check_password_hash
from models import Clients, Template, User, Lite

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
    
    @app.route("/login2/", methods=["GET", "POST"])
    def login2():
        # временно, объединить!
        if request.method == "GET":
            response = Template(title='Авторизация', info="Пройдите регистрацию и начните тестирование ваши навыки", subinfo='Провертье свои знания', user=None)
            return render_template("index2.html", nav_u=None)
        elif request.method == "POST":
            name = request.form.get('login')
            pasw = request.form.get('password')
            uname = Clients.query.filter(Clients.name == name).first()

            if check_password_hash(uname.password, pasw):
                login_user(uname)
                return redirect(url_for('profile'))
            else:
                return "Failed"

    @app.route("/sign2", methods=["GET", "POST"])
    def sign2():
        # временно, объединить!
        if request.method == "GET":
            response = Template(title='Регистрация', info="Пройдите регистрацию и начните тестирование ваши навыки", subinfo='Провертье свои знания', user=None)
            return render_template("index2.html", nav_u=None)
        elif request.method == "POST":
            uname = request.form.get("login")
            email = request.form.get("email")
            sump = generate_password_hash(request.form.get('password'))

            c = Clients(name=uname, email=email, password=sump)
            db.session.add(c)
            db.session.flush()
            db.session.commit()
            return redirect(url_for('profile'))

    @app.route("/")
    def index():
        '''Главная страница'''
        response = Template(title='Авторизация', info="Пройдите регистрацию и начните тестирование ваши навыки", subinfo='Провертье свои знания', user=None)
        if 'username' in session or request.cookies.get('username'):
            return redirect(url_for('profile'))
        # временно
        return render_template('index2.html', response=response, nav_u=None)

    @app.route("/sign", methods=['POST', 'GET'])
    def signup():
        '''Маршрут регистрации'''
        if request.method == 'POST':
            login = request.form.get('login') # name
            email = request.form.get('email')
            sump = generate_password_hash(request.form.get('password'))

            if Clients.query.filter(Clients.name == login).count() == 0:
                try:
                    c = Clients(name=login, email=email, password=sump)
                    db.session.add(c)
                    db.session.flush()
                    db.session.commit()
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

    @app.route("/login", methods=['POST', 'GET'])
    def login():
        '''Маршрут авторизации'''
        if 'username' in session or request.cookies.get('username'):
            return redirect(url_for('profile'))

        if request.method == 'POST':		
            name = request.form.get('login')
            pasw = request.form.get('password')
            sql  = Clients.query.filter(Clients.name == name)

            if sql.count() != 0:
                if check_password_hash(sql[0].password, pasw):
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

    @app.route("/profile")
    def profile():
        '''Страница профиля'''
        name = session.get('username') or request.cookies.get('username')
        if name:
            sql = Clients.query.filter(Clients.name == name)
            lite = Lite(name=name, lvl=sql[0].level, loged=True)
            user = User(
                name=name, email=sql[0].email,
                lvl=sql[0].level, solved=sql[0].solved,
                tasks_id=sql[0].tasks_id, date=sql[0].date)
            response = Template(title="Профиль", info='Профиль', subinfo=name, user=user)
            return render_template('profile.html', response=response, nav_u=lite)
        return redirect(url_for('index'))

    @app.route("/logout")
    def logout():
        '''Маршрут деавторизации'''
        logout_user()
        try:
            if 'username' in session:
                session.pop('username', None)
            if request.cookies.get('username'):
                resp = make_response(redirect(url_for('index')))
                resp.delete_cookie('username')
                return resp
            return redirect(url_for('index'))
        except:
            pass

    @app.route("/profile/<int:n>")
    @app.route("/profile/<n>")
    def client(n):
        '''Страницы др. пользователей'''
        if type(n) is int:
            sql = Clients.query.filter(Clients.id == n)
        else: sql = Clients.query.filter(Clients.name == n)
        if sql.count() != 0:
            lite = Lite(name=session['username'], lvl=session['lvl'], loged=session['loged'])
            user = User(
                name=sql[0].name, email=sql[0].email,
                lvl=sql[0].level, solved=sql[0].solved,
                tasks_id=sql[0].tasks_id, date=sql[0].date,)
            response = Template(title=sql[0].name, info='Профиль', subinfo=sql[0].name, user=user)
            return render_template('profile.html', response=response, nav_u=lite)
        abort(404, description="This user not exists")

    @app.errorhandler(404)
    def resource_not_found(e):
        '''Страница 404'''
        return str(e), 404

    @app.route("/help")
    def help():
        '''Страница помощи'''
        response = Template(title='Помощь', info="Помощь", subinfo="Эта страница ещё в разработке", user=None)
        return render_template('other.html', response=response, nav_u=None)

    @app.route("/about")
    def about():
        '''Информационная страница'''
        response = Template(title='Об Сервисе', info="Об Сервисе", subinfo="Эта страница ещё в разработке", user=None)
        return render_template('other.html', response=response, nav_u=None)