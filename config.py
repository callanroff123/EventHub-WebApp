import os
from dotenv import load_dotenv


load_dotenv()
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    PROJECT_NAME = "Extracting-Music-Events"
    SECRET_KEY = os.environ.get("SECRET_KEY") or "xxxx"
    MAIL_SERVER = os.environ.get("MAIL_SERVER")
    MAIL_PORT = int(os.environ.get("MAIL_PORT") or 25)
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS") is not None
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    ADMINS = ["calwebscraper@gmail.com"]
    MS_TRANSLATOR_KEY = os.environ.get("MS_TRANSLATOR_KEY")
    GMAIL_USER_EMAIL = os.environ.get("GMAIL_USER_EMAIL")
    GMAIL_PASSWORD = os.environ.get("GMAIL_USER_PASSWORD")
    GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD")
    RECAPTCHA_PUBLIC_KEY = os.environ.get("RECAPTCHA_PUBLIC_KEY")
    RECAPTCHA_SECRET_KEY = os.environ.get("RECAPTCHA_SECRET_KEY")
    ENV = os.environ.get("ENV")