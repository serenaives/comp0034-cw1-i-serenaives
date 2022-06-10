import dash
from flask import Flask
from flask.helpers import get_root_path
from flask_login import login_required

from config import DevelopmentConfig


def create_app():
    server = Flask(__name__)
    server.config.from_object(DevelopmentConfig)

    register_dashapp(server)
    register_extensions(server)
    register_blueprints(server)

    return server


def register_dashapp(app):
    from dashboard.layout import layout
    from dashboard.callbacks import register_callbacks

    # Meta tags for viewport responsiveness
    meta_viewport = {
        "name": "viewport",
        "content": "width=device-width, initial-scale=1, shrink-to-fit=no"}

    dashapp1 = dash.Dash(__name__,
                         server=app,
                         url_base_pathname='/dashboard/',
                         assets_folder=get_root_path(__name__) + '/dashboard/assets/',
                         meta_tags=[meta_viewport])

    with app.app_context():
        dashapp1.title = 'Dashapp 1'
        dashapp1.layout = layout
        register_callbacks(dashapp1)

    _protect_dashviews(dashapp1)


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
    from coursework_2 import server_bp

    server.register_blueprint(server_bp)