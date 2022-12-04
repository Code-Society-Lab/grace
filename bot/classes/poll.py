from collections import namedtuple
from discord import Member
from typing import List, Dict, Optional

Option = namedtuple("Option", ["title", "emoji"])


class Poll:
	def __init__(self, options: List[Option], title: str):
		self.title: str = title

		self.__selected_option_by_users: Dict[Member, Option] = {}
		self.__options: List[Option] = options
		self.__counter: Dict[Option, int] = {}

		for option in self.__options:
			self.__counter[option] = 0

	@property
	def options(self) -> List[Option]:
		return self.__options

	@property
	def counter(self) -> Dict[Option, int]:
		return self.__counter

	@property
	def winner(self) -> Optional[Option]:
		""" Returns the winner option. None if no one voted

		 	:rtype: Option | None
		 """
		if max(self.__counter.values()) > 0:
			return max(self.__counter, key=self.__counter.get)

	def _increment_counter(self, option: Option) -> None:
		""" Increment option counter

			:param option: Poll option
		"""
		self.__counter[option] += 1

	def _decrement_counter(self, option: Option) -> None:
		""" Decrement option counter

			:param option: Poll option
		"""
		self.__counter[option] -= 1

	def set_user_option(self, member: Member, option: Option) -> None:
		""" Sets user's chosen option

			:param member: User
			:param option: Corresponding option that the user chose
		"""
		current_option = self.selected_option_for(member)

		if current_option:
			self._decrement_counter(current_option)

		self._increment_counter(option)
		self.__selected_option_by_users[member] = option

	def has_user_voted(self, member: Member) -> bool:
		""" Checks if user has voted

			:param member: User
			:rtype: bool
		"""
		if member in self.__selected_option_by_users:
			return True
		return False

	def selected_option_for(self, member: Member) -> Option:
		""" Returns the option that the user chose

			:param member: User
			:rtype: Option
		"""
		return self.__selected_option_by_users.get(member)
