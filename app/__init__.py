from flask import Flask, request, current_app
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap
from flask_moment import Moment
import logging
from logging.handlers import SMTPHandler
import os


# Extensions will be initalised after creating an instance of the application
# I.e., after "create_app()" is called
db = SQLAlchemy()
migrate = Migrate()
bootstrap = Bootstrap()
moment = Moment() # Converts UTC time to the specific client's local time. Works together with moment.js => Call in <scripts> tag in HTML.


# "FACTORY FUNCTION"
# Instead of setting app as a global variable (i.e., declaring outside of this function), have a function which creates an instance of the app instead
# Makes it easier to test under different configurations, and allow multiple instantiations of the app simultaneously, in isolation
def create_app(config_class = Config):

    app = Flask(__name__)
    app.config.from_object(config_class)

    # Uncomment these when we integrate a database with the app
    #db.init_app(app)
    #migrate.init_app(app, db)
    bootstrap.init_app(app)
    moment.init_app(app) # Converts UTC time to the specific client's local time. Works together with moment.js => Call in <scripts> tag in HTML.

    # Send error logs to an email
    if (not app.debug) and (not app.testing):
        if app.config["MAIL_SERVER"]:
            auth = None
            if app.config["MAIL_USERNAME"] or app.config["MAIL_PASSWORD"]:
                auth = (app.config["MAIL_USERNAME"], app.config["MAIL_PASSWORD"])
            secure = None
            if app.config["MAIL_USE_TLS"]:
                secure = ()
            mail_handler = SMTPHandler(
                mailhost = (app.config["MAIL_SERVER"], app.config["MAIL_PORT"]),
                fromaddr = f"no-reply@{app.config['MAIL_SERVER']}",
                toaddrs = app.config["ADMINS"],
                subject = f"{app.config['PROJECT_NAME']} Failure :/",
                credentials = auth,
                secure = secure
            )
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)

    # Register errors blueprint with the app
    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    # Register application-specific blueprint with the app
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    return(app)