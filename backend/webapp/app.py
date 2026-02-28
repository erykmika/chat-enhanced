from flask import Flask
from flask_cors import CORS

from backend.webapp.auth.infrastructure.api import auth_bp
from backend.webapp.chat.api import chat_bp
from backend.webapp.config import FLASK_CONFIG
from backend.webapp.database import db
from backend.webapp.mails import mailing

app = Flask(__name__)

app.config.update(FLASK_CONFIG)

db.init_app(app)
mailing.init_app(app)

app.register_blueprint(auth_bp)
app.register_blueprint(chat_bp)

CORS(app)


@app.route("/")
def index():
    return "Welcome to the Web App!"


@app.route("/health")
def health():
    return {"status": "ok"}, 200
