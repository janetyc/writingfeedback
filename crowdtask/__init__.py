from flask import Flask, url_for, redirect
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
app = Flask(__name__)
def create_app(env):
    #app = Flask(__name__)

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
    

    #should put after app
    from crowdtask.views import views
    from crowdtask.api import api
    
    app.register_blueprint(views)
    app.register_blueprint(api)

    db.init_app(app)

    return app

#@app.route("/")
#def index():
#    return redirect(url_for('views.index'))
#
#@app.errorhandler(404)
#def page_not_found(error):
#    return redirect(url_for('views.page_not_found'))
#
#@app.errorhandler(400)
#def bad_request(error):
#    return redirect(url_for('views.bad_request'))