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


# For Artist popularity bar functionality!
def followers_bar(rank, max_rank):
    try:
        rank = float(rank)
        percent = 1 - rank / max_rank
        r_start, g_start, b_start = 0, 70, 255
        r_end, g_end, b_end = 200, 230, 255
        r = int(r_start + (1 - percent) * (r_end - r_start))
        g = int(g_start + (1 - percent) * (g_end - g_start))
        b = int(b_start + (1 - percent) * (b_end - b_start))
        color = f'rgb({r}, {g}, {b})'
        bar_width = percent * 100
        return f'''
            <div style="width:100px; height:10px; border-radius:5px;" data-score="{bar_width}">
                <div style="background:{color}; width:{bar_width}%; height:100%; border-radius:5px;"></div>
            </div>
        '''
    except:
        return ''


# "FACTORY FUNCTION"
# Instead of setting app as a global variable (i.e., declaring outside of this function), have a function which creates an instance of the app instead
# Makes it easier to test under different configurations, and allow multiple instantiations of the app simultaneously, in isolation
def create_app(config_class = Config):

    app = Flask(__name__)
    app.config.from_object(config_class)
    app.jinja_env.globals.update(followers_bar = followers_bar)

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