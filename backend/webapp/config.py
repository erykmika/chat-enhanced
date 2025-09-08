import os

from dotenv import load_dotenv

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET", "123somerandomjwtsecret123")

POSTGRES_DB = os.getenv("POSTGRES_DB", "devdb")
POSTGRES_USER = os.getenv("POSTGRES_USER", "devuser")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "devpass")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

SQLALCHEMY_DATABASE_URI = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

FLASK_CONFIG = {"SQLALCHEMY_DATABASE_URI": SQLALCHEMY_DATABASE_URI}
