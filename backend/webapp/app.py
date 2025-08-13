from flask import Flask
from backend.webapp.config import FLASK_CONFIG
from backend.webapp.database import db

app = Flask(__name__)

app.config.update(FLASK_CONFIG)

db.init_app(app)