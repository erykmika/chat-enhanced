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

MAIL_CONFIG = {
    "MAIL_USERNAME": os.getenv("MAIL_USERNAME"),
    "MAIL_PASSWORD": os.getenv("MAIL_PASSWORD"),
    "MAIL_DEFAULT_SENDER": os.getenv("MAIL_DEFAULT_SENDER", "chat@mail.int"),
    "MAIL_PORT": os.getenv("MAIL_PORT"),
    "MAIL_SERVER": os.getenv("MAIL_SERVER"),
}
CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "*")

FLASK_CONFIG = {
    "SQLALCHEMY_DATABASE_URI": SQLALCHEMY_DATABASE_URI,
    "CORS_ORIGINS": CORS_ALLOWED_ORIGINS,
    **MAIL_CONFIG,
}

FRONTEND_ROOT_DOMAIN = os.getenv("FRONTEND_ROOT_DOMAIN", "")
