from sqlalchemy import Column, Integer, String
from bot import app
from db.model import Model


class WordleWords(app.base, Model):
	__tablename__ = 'wordle_words'

	id = Column(Integer, primary_key=True)
	word = Column(String(255), unique=True)
