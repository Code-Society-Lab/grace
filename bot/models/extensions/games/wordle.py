from sqlalchemy import Column, Integer, String, DateTime
from bot.models.extensions.games.wordle_words import WordleWords
from sqlalchemy.orm import relationship
from bot import app
from db.model import Model
from datetime import datetime


class Wordle(app.base, Model):
	__tablename__ = 'wordle'

	id = Column(Integer, primary_key=True)
	user_id = Column(String, nullable=False)
	points = Column(Integer, nullable=False)
	play_date = Column(DateTime, nullable=False)

	@classmethod
	def add_user(cls, user_id: str, points: int, date: datetime, id: int) -> None:
		Wordle(user_id=user_id, play_date=date, points=points, id=id).save()

	@classmethod
	def update_user(cls, user_id: str, points: int, date: datetime) -> None:
		user = cls.get_by(user_id=user_id)
		user.points = user.points + points
		user.play_date = date

	@classmethod
	def update_database(cls, user_id: str, points: int):
		user = cls.get_by(user_id=user_id)
		if user is not None:
			cls.update_user(user_id, points, datetime.now())
			cls.create()
		else:
			last_id = cls.query().order_by(Wordle.id.desc()).first()
			if last_id is None:
				last_id = 0
			cls.add_user(user_id, points, datetime.now(), last_id + 1)
