from flask import Flask, render_template

from .database import init_engine, session, metadata
from .converters import register_converters


def create_app():
    app = Flask(__name__)
    app.config.from_object('polipoly2.default_settings')
    app.config.from_envvar('POLIPOLY2_SETTINGS', silent=True)

    register_converters(app)

    init_engine(app.config['DATABASE_URI'])

    def shutdown_session(response):
        session.remove()
        return response

    app.after_request(shutdown_session)

    from polipoly2.views import views
    app.register_module(views)

    return app
