from sqlalchemy import Column, Integer, DateTime
from bot import app
from db.model import Model
from datetime import datetime


class Wordle(app.base, Model):
	__tablename__ = 'wordle'

	id = Column(Integer, primary_key=True)
	member_id = Column(Integer, nullable=False, unique=True)
	points = Column(Integer, nullable=False)
	play_date = Column(DateTime, nullable=False)

	@classmethod
	def update_database(cls, member_id: int, points: int):
		user = cls.get_by(member_id=member_id)
		if user is not None:
			user.points += points
			user.play_date = datetime.now()
			user.save()
		else:
			cls.create(
				member_id=member_id,
				points=points,
				play_date=datetime.now()
			)
