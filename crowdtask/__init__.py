import os
import config
from flask import Flask, url_for, redirect, request
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

def datetimeformat(value, format='[%Y-%m-%d %H:%M]'):
    return value.strftime(format)

def url_for_other_page(page):
    args = request.view_args.copy()
    args['page'] = page
    return url_for(request.endpoint, **args)

def create_app():

    app = Flask(__name__)
    env = os.getenv('ENV')

    if env == "DEVELOPMENT":
        app.config.from_object('config.DevelopmentConfig')
    elif env == "PRODUCTION":
        app.config.from_object('config.ProductionConfig')
    elif env == "TESTING":
        app.config.from_object('config.TestingConfig')
    elif env == "DEBUG":
        app.config.from_object('config.DebugConfig')
    else:
        app.config.from_object('config.Config')

    app.jinja_env.filters['datetimeformat'] = datetimeformat
    app.jinja_env.globals['url_for_other_page'] = url_for_other_page

    #should put after app
    from crowdtask.views import views
    from crowdtask.api import api
    from crowdtask.task_views import task_views
    from crowdtask.vis_views import vis_views
    from crowdtask.admin_views import admin_views

    app.register_blueprint(views)
    app.register_blueprint(api)
    app.register_blueprint(task_views)
    app.register_blueprint(vis_views)
    app.register_blueprint(admin_views)

    db.app = app
    db.init_app(app)

    with app.app_context():
        # Extensions like Flask-SQLAlchemy now know what the "current" app
        # is while within this block. Therefore, you can now run........
        db.create_all()

    return app


