from discord import Member
from typing import List, Dict, Optional

class PollModel:
	def __init__(
			self,
			options: List[str],
			emojis: List[str],
			allowed_emoji_size: int,
			counter: Dict,
			title: str
	):
		self._voted_users: Dict[Member, str] = {}
		self._poll_options: List[str] = options
		self._poll_emojis: List[str] = emojis
		self._poll_counter: Dict[str, int] = counter
		self._poll_title: str = title
		self._allowed_emoji_size: int = allowed_emoji_size
		self._timer_label: Optional[str] = None

	@property
	def timer_label(self):
		return self._timer_label

	@timer_label.setter
	def timer_label(self, new_label: str):
		self._timer_label = new_label

	@property
	def title(self):
		return self._poll_title

	@property
	def options(self):
		return self._poll_options

	@property
	def emojis(self):
		return self._poll_emojis

	@property
	def counter(self):
		return self._poll_counter

	@property
	def allowed_emoji_size(self):
		return self._allowed_emoji_size

	def increment_counter(self, emoji: str) -> None:
		""" Increment emoji counter
			:param emoji: Emoji string
		"""
		self._poll_counter[emoji] += 1

	def decrement_counter(self, emoji: str) -> None:
		""" Decrement emoji counter
			:param emoji: Emoji string
		"""
		self._poll_counter[emoji] -= 1

	def set_user(self, user: Member, emoji: str) -> None:
		""" Set user's vote choice
			:param user: User
			:param emoji: Corresponding emoji that the user chose
		"""
		self._voted_users[user] = emoji

	def get_user_emoji(self, user: Member) -> str:
		""" Get user's voted option
			:param user: User
			:return: Returns emoji that the user chose
		"""
		return self._voted_users[user]

	def user_has_voted(self, user: Member) -> bool:
		if user in self._voted_users:
			return True
		return False