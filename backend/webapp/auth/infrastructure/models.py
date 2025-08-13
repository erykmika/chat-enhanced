from sqlalchemy.orm import mapped_column

from backend.webapp.database import db


class User(db.Model):
    id: int = mapped_column(primary_key=True)
    email: str = mapped_column(unique=True)
    password: str = mapped_column(nullable=False)
    role: str = mapped_column(nullable=False)
