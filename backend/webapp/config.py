import os

from dotenv import load_dotenv

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET")

FLASK_CONFIG = {
    "SQLALCHEMY_DATABASE_URI" : "sqlite:///chat.db"
}