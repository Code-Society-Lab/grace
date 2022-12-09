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

	# @classmethod
	# def add_user(cls, user_id: str, points: int, date: datetime, id: int) -> None:
	# 	Wordle(user_id=user_id, play_date=date, points=points, id=id).save()

	# @classmethod # Unnecessary function
	# def update_user(cls, user_id: str, points: int, date: datetime) -> None:
	# 	user = cls.get_by(user_id=user_id)
	# 	user.points = user.points + points
	# 	user.play_date = date
	# 	user.save()

	@classmethod
	def update_database(cls, member_id: int, points: int):
		user = cls.get_by(member_id=member_id)
		if user is not None:
			user.points += points
			user.play_date = datetime.now()
			user.save()
			# cls.update_user(member_id, points, datetime.now())
			# cls.create()
		else:
			cls.create(
				member_id=member_id,
				points=points,
				play_date=datetime.now()
			)
			# last_id = cls.query().order_by(Wordle.id.desc()).first()
			# if last_id is None:
			# 	last_id = 0
			# cls.add_user(member_id, points, datetime.now(), last_id + 1)
