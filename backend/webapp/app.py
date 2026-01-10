from flask import Flask

from backend.mails import mailing
from backend.webapp.auth.infrastructure.api import auth_bp
from backend.webapp.config import FLASK_CONFIG
from backend.webapp.database import db

app = Flask(__name__)

app.config.update(FLASK_CONFIG)

db.init_app(app)
mailing.init_app(app)

app.register_blueprint(auth_bp)


@app.route("/")
def index():
    return "Welcome to the Web App!"
