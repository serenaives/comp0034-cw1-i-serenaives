from datetime import date
from flask import Blueprint
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask import session
from flask import flash
from flask_login import current_user
from flask_login import login_required
from flask_login import login_user
from flask_login import logout_user
from werkzeug.urls import url_parse

from coursework_2.extensions import db
from coursework_2.forms import LoginForm, RegistrationForm, QuestionForm
from coursework_2.models import User, Questions, Highscores

server_bp = Blueprint('main', __name__)


@server_bp.route('/')
def index():
    return render_template("index.html", title='Home Page')


@server_bp.route('/login/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            error = 'Invalid username or password'
            return render_template('login.html', form=form, error=error)

        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')

        return redirect(next_page)

    return render_template('login.html', title='Sign In', form=form)


@server_bp.route('/logout/')
@login_required
def logout():
    session.clear()
    logout_user()
    flash('Successfully logged out')
    return redirect(url_for('main.index'))


@server_bp.route('/register/', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        # initialise new user's highscores to zero
        user.highscore = 0
        db.session.add(user)
        db.session.commit()

        return redirect(url_for('main.login'))

    return render_template('register.html', title='Register', form=form)


@server_bp.route('/quiz_home/')
def quiz_home():
    session['marks'] = 0
    session['new_highscore'] = False
    session['used_hint'] = False
    return render_template("quiz_home.html", title='Quiz Home')


@server_bp.route('/quiz_play/<int:id>', methods=['GET', 'POST'])
@login_required
def quiz_play(id):
    form = QuestionForm()
    q = Questions.query.filter_by(q_id=id).first()

    if not q:
        return redirect(url_for('main.quiz_end'))

    if request.method == 'POST':
        # user has submitted the form via POST request
        try:
            option = request.form['options']
            # award 3 points if correct answer was submitted
            if option == q.ans:
                session['marks'] += 3
        except KeyError:
            # if no answer, do not update score
            pass
        # penalise if hint was used
        if session['used_hint']:
            session['marks'] -= 1
            session['used_hint'] = False

        return redirect(url_for('main.quiz_play', id=(id + 1)))

    form.options.choices = [(q.option_a, q.option_a), (q.option_b, q.option_b),
                            (q.option_c, q.option_c)]
    return render_template('quiz_play.html', form=form, q=q, title='Quiz Play Question {}'.format(id))


@server_bp.route('/use_hint/')
def use_hint():
    session['used_hint'] = True
    # do not navigate away from current page: HTTP response code 204
    return '', 204


@server_bp.route('/quiz_end/')
def quiz_end():
    session["score"] = session['marks']
    session['new_highscore'] = current_user.update_highscore(session["score"])
    session["highscore"] = current_user.highscore
    return render_template("quiz_end.html", title='Quiz End')


@server_bp.route('/leaderboard_home/')
def leaderboard_home():
    return render_template("leaderboard_home.html", title='Leaderboard Home')


@server_bp.route('/leaderboard_active/', methods=['GET', 'POST'])
@login_required
def leaderboard_active():
    if current_user.is_authenticated:
        return render_template("leaderboard_active.html", title='Leaderboard Active')
