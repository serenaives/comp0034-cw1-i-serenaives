import dash
from flask import Flask
from flask.helpers import get_root_path
from flask_login import login_required
import dash_bootstrap_components as dbc
from flask_bootstrap import Bootstrap
from flask_admin import Admin


def create_app(Config):
    server = Flask(__name__)
    server.config.from_object(Config)

    register_dashapp(server)
    register_extensions(server)
    register_blueprints(server)

    with server.app_context():
        from coursework_2.models import User
        from coursework_2.extensions import db
        db.create_all()

    bootstrap = Bootstrap(server)

    return server


def register_dashapp(app):
    # access Dash app via Flask route

    from coursework_2.dashboard.layout import layout
    from coursework_2.dashboard.callbacks import register_callbacks

    # Meta tags for viewport responsiveness
    meta_viewport = {
        "name": "viewport",
        "content": "width=device-width, initial-scale=1, shrink-to-fit=no"}

    dashapp = dash.Dash(__name__,
                        server=app,
                        url_base_pathname='/dashboard/',
                        assets_folder=get_root_path(__name__) + '/dashboard/assets/',
                        meta_tags=[meta_viewport],
                        external_stylesheets=[dbc.themes.MINTY],
                        suppress_callback_exceptions=True
                        )

    with app.app_context():
        dashapp.title = 'Dashapp 1'
        dashapp.layout = layout
        register_callbacks(dashapp)

    _protect_dashviews(dashapp)


def _protect_dashviews(dashapp):
    for view_func in dashapp.server.view_functions:
        if view_func.startswith(dashapp.config.url_base_pathname):
            dashapp.server.view_functions[view_func] = login_required(
                dashapp.server.view_functions[view_func])


def register_extensions(server):
    from coursework_2.extensions import db
    from coursework_2.extensions import login
    from coursework_2.extensions import migrate

    db.init_app(server)
    login.init_app(server)
    login.login_view = 'main.login'
    migrate.init_app(server, db)


def register_blueprints(server):
    from coursework_2.webapp import server_bp

    server.register_blueprint(server_bp)


def update_highscores(user_id, new_highscore):
    from coursework_2.models import Highscores
    from coursework_2.extensions import db
    from datetime import date

    hs = Highscores.query.filter_by(user_id=user_id)
    if hs.count() > 0:
        # there is already a Highscores record corresponding to current user
        hs.update(dict(value=new_highscore, date=date.today()))
    else:
        # new Highscores record needs to be created
        hs_new = Highscores(user_id=user_id, value=new_highscore, date=date.today())
        db.session.add(hs_new)
    db.session.commit()
