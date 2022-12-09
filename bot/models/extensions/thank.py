from typing import Optional
from sqlalchemy import Column, Integer
from bot import app
from db.model import Model


class Thank(app.base, Model):
	__tablename__ = 'thanks'

	id = Column(Integer, primary_key=True)
	member_id = Column(Integer, nullable=False, unique=True)
	count = Column(Integer, default=0)

	@property
	def rank(self) -> Optional[str]:
		if self.count in range(1, 11):
			return 'Intern'
		elif self.count in range(11, 21):
			return 'Helper'
		elif self.count in range(21, 31):
			return 'Vetted helper'
		elif self.count > 30:
			return 'Expert'
		else:
			return None