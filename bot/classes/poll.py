from collections import namedtuple
from discord import Member, User
from typing import List, Dict, Optional, Union

Option = namedtuple("Option", ["title", "emoji"])


class Poll:
	"""Represent a Poll with multiple given options

	:param options: The list of options in the poll
	:type options: List[Option]

	:param title: The poll title
	:type title: str
	"""
	def __init__(self, options: List[Option], title: str):
		self.title: str = title

		self.__selected_option_by_users: Dict[Member, Option] = {}
		self.__options: List[Option] = options
		self.__counter: Dict[Option, int] = {}

		for option in self.__options:
			self.__counter[option] = 0

	@property
	def options(self) -> List[Option]:
		"""Returns the poll's options"""
		return self.__options

	@property
	def counter(self) -> Dict[Option, int]:
		"""Returns the options counter"""
		return self.__counter

	@property
	def winner(self) -> Optional[Option]:
		"""Returns the winner option. None if no one voted

		:return: The option who has the highest count or None if none has any vote
		:rtype: Option | None
		"""
		if max(self.__counter.values()) > 0:
			return max(self.__counter, key=self.__counter.get)

	def _increment_counter(self, option: Option) -> None:
		"""Increment option counter

		:param option: Poll option
		:type option: Option
		"""
		self.__counter[option] += 1

	def _decrement_counter(self, option: Option) -> None:
		"""Decrement option counter

		:param option: Poll option
		:type option: Option
		"""
		self.__counter[option] -= 1

	def set_user_option(self, user_or_member: Union[User, Member], option: Option) -> None:
		"""Sets user's chosen option

		:param user_or_member: A member
		:type: member: Member

		:param option: Corresponding option that the user chose
		:type option: Option
		"""
		current_option = self.selected_option_for(user_or_member)

		if current_option:
			self._decrement_counter(current_option)

		self._increment_counter(option)
		self.__selected_option_by_users[user_or_member] = option

	def has_user_voted(self, member: Member) -> bool:
		"""Checks if member has voted

		:param member: A member
		:type member: Member

		:returns: True if the Member has voted otherwise False
		:rtype: bool
		"""
		if member in self.__selected_option_by_users:
			return True
		return False

	def selected_option_for(self, member: Union[User, Member]) -> Option:
		"""Returns the option that the user chose

		:param member: A member
		:type member: Member

		:return: An option
		:rtype: Option
		"""
		return self.__selected_option_by_users.get(member)
