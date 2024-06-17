from models import Clients, Template, User
from models import Lengs # Remove

from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired

from flask_login import login_user, logout_user, current_user, login_required, AnonymousUserMixin
from flask import (
	url_for, redirect,
	render_template,
	session, request,
	flash, make_response,
	abort
)

def users_routes(app, db, login, mail):
    '''Инициализация пользовательских маршрутов'''

    urlsafe = URLSafeTimedSerializer(app.config['SECRET_KEY'])

    def send_mail(email) -> bool:
        # redirect на регистрацию, пользователь не верифицирован
        try:
            token = urlsafe.dumps(email, salt='email-confirm')
            msg = Message(
                "Confirm Email",
                sender="noreply@app.com",
                recipients=[email],
                body="Confirm Link"
            )

            data = {
                "app_name": "Codify",
                "title": "Confirm Email",
                "body": f"Your link is",
                "link": url_for("confirm", token=token, _external=True)
            }

            msg.html = render_template("mail.html", data=data)

            mail.send(msg)
        except Exception as e:
            return False
        return True


    # NOT USE
    def userOnline() -> None: # Пользователь в сети
        if current_user != AnonymousUserMixin:
            usr = Clients.query.filter(Clients.id==current_user.id)
            usr.status = 1
            db.session.add(usr)
            db.session.flush()
            db.session.commit()
    
    # NOT USE
    def allUserOffline() -> None: # Все пользователи становятся оффлайн
        usrs = Clients.query.all()
        for usr in usrs:
            if usr.status == 1:
                usr.status = 0
                db.session.add(usr)
                db.session.flush()
                db.session.commit()

    # NOT USE
    @app.route("/highlight")
    def highlight():
        lengs = Lengs.query.all()
        response = Template(title='Highlight', info="Testing highlight", subinfo='highlight')
        return render_template("highlight.html", response=response, lengs=lengs)

    # NOT USE
    @app.route("/test/<name>")
    @login_required
    def test(name: str): return str(Clients.query.filter(Clients.name == name).count())


    @login.user_loader
    def load_user(uid): return Clients.query.get(uid)

    @login.unauthorized_handler
    def unauthorized_handler():
        response = Template(title='Не зарегистрированное обращение', info="Не зарегистрированное обращение!", subinfo='Зарегистрируйтесь для обращения!', user=None)
        return render_template("index.html", response=response)

    @app.errorhandler(404)
    def resource_not_found(e):
        '''Страница 404'''
        response = Template(title='Ошибка 404', info=str(e))
        return render_template('other.html', response=response)
    
    @app.route("/")
    def index():
        '''Главная страница'''
        response = Template(title='Авторизация', info="Пройдите регистрацию и начните тестирование ваши навыки", subinfo='Провертье свои знания')
        if 'username' in session or request.cookies.get('username'):
            return redirect(url_for('profile'))
        resp = make_response(render_template('index.html', response=response))
        resp.set_cookie('auth', "null") # так же имеет username
        return resp

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
                usr = sql.first()
                if usr.auth == 1:
                    if usr.verify_password(pasw):
                        login_user(usr)
                        session['username'] = name

                        if request.form.get('setcookies'):
                            resp = make_response(redirect(url_for('profile')))
                            resp.set_cookie('username', name)
                            return resp
                        
                        return redirect(url_for('profile'))
                    else:
                        flash('Password: неверный пароль!')
                else:
                    flash('Email Verification: Не верифицированная почта!')
            else:
                flash('Login: такой пользователь не существует!')
            return redirect(url_for('index'))
        else:
            response = Template(title='Авторизация')
            if 'username' in session or request.cookies.get('username'):
                return redirect(url_for('profile'))
            return render_template('login.html', response=response)
                
    @app.route("/sign", methods=["GET", "POST"])
    def signup():
        '''Маршрут регистрации'''
        if 'username' in session or request.cookies.get('username'):
            return redirect(url_for('profile'))
        
        if request.method == "POST":
            uname = request.form.get("login")
            email = request.form.get("email")
            passw = request.form.get('password')

            if (
                Clients.query.filter(Clients.name == uname).count() == 0 and
                Clients.query.filter(Clients.email == email).count() == 0
            ):
                try:
                    send_mail(email=email)

                    # Создание пользователя и добавление в БД
                    c = Clients(name=uname, email=email)
                    c.password(passw)
                    db.session.add(c)
                    db.session.flush()
                    db.session.commit()

                    if request.form.get('setcookies'):
                        resp = make_response(redirect(url_for('profile')))
                        resp.set_cookie('username', login)
                        return resp

                    flash('Email Verification: Откройте почту для верификации почты!', 'info')
                except Exception as e:
                    db.session.rollback()
                    app.logger.info('Ошибка добавления в БД: %s' % e)
            else:
                flash('Такой пользователь уже существует!', 'warning')

        return redirect(url_for('index'))

    @app.route("/confirm/<token>")
    def confirm(token: str):
        try:
            email = urlsafe.loads(token, salt='email-confirm', max_age=3600)
            usr   = Clients.query.filter(Clients.email == email)
            if usr.count() == 1:
                usr = usr.first()
                usr.auth = 1 if usr.auth == 0 else usr.auth
                db.session.add(usr)
                db.session.flush()
                db.session.commit()
        except SignatureExpired:
            flash('Токен устарел!', 'warning')
            return redirect(url_for('index'))
        # возвращаем ответ на верификацию и перенаправляем в профиль пользователя
        return f"Пользователь верифицирован! { email }", {"Refresh": f"3; url={ url_for('profile') }"}

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

    @app.route("/profile")
    @login_required
    def profile():
        '''Страница профиля'''
        # name = session.get('username') or request.cookies.get('username')
        # if name:
        response = Template(title="Профиль", info='Профиль')
        resp = make_response(render_template('profile.html', response=response))
        resp.set_cookie('username', current_user.name)
        return resp

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
        abort(404, description="Такого пользователя нет!")

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