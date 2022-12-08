from sqlalchemy import Column, Integer, String
from bot import app
from db.model import Model


class Thank(app.base, Model):
	__tablename__ = 'thank'

	id = Column(Integer, primary_key=True)
	member_id = Column(String)
	thank_count = Column(Integer)

	@classmethod
	def add_member(cls, member_id: str, thank_count: int):
		cls(
			member_id=member_id,
			thank_count=thank_count,
			id=cls.get_last_id()
		).save()

	@classmethod
	def remove_member(cls, member_id: str):
		member = cls.get_by(member_id=member_id)
		cls.delete(member)

	@classmethod
	def increment_member_thank_count(cls, member_id: str):
		member = cls.get_by(member_id=member_id)
		member.thank_count += 1
		cls.create()

	@classmethod
	def retrieve_member_thank_count(cls, member_id: str) -> int:
		member = cls.get_by(member_id=member_id)
		return member.thank_count

	@classmethod
	def does_member_exist(cls, member_id: str) -> bool:
		member = cls.get_by(member_id=member_id)
		if member is None:
			return False
		return True

	@classmethod
	def get_last_id(cls) -> int:
		last_id = cls.query().order_by(cls.id.desc()).first()
		return 0 if last_id is None else last_id


