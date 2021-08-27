from sqlalchemy import Column, Integer, String
from bot import app
from db.model import Model


class Answer(app.base, Model):
    """Answer model (With SQLAlchemy ORM)"""
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True)
    answer = Column(String, nullable=False)

