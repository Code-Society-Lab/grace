from sqlalchemy import Column, Integer, String
from grace.model import Model
from bot import app


class Answer(app.base, Model):
    """Answer model (With SQLAlchemy ORM)"""
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True)
    answer = Column(String(255), nullable=False)
