from functools import partial
from typing import Callable, Optional, Any, List
from bot.extensions.command_error_handler import send_command_help
from collections.abc import Sequence
from discord.ext.commands import Cog, Context, hybrid_group
from discord import Embed, ButtonStyle, Interaction, Message
from discord.ui import Button
from asyncio import TimeoutError
from bot.grace import Grace
from lib.timed_view import TimedView
from bot.classes.poll import Poll, Option


async def create_poll_embed(poll: Poll) -> Embed:
	""" Returns a newly created poll embed

		:param poll: A Poll
		:returns: Created embed
		:rtype: Embed

	"""
	description: str = "{timer}\n\n"

	for option in poll.options:
		description += f"{option.emoji} **{option.title}**: {poll.counter[option]}\n\n"

	return Embed(title=poll.title, description=description)


class PollView(TimedView):
	def __init__(self, poll: Poll, embed: Embed, winner_callback: Callable, seconds: int):
		super().__init__(seconds)

		self.__poll: Poll = poll
		self.__embed: Embed = embed
		self.__winner_callback: Callable = winner_callback
		self.__message: Optional[Message] = None

	@property
	def poll(self) -> Poll:
		return self.__poll

	@property
	def message(self) -> Optional[str]:
		return self.__message

	@message.setter
	def message(self, message):
		if self.__message is None:
			self.__message = message

	def add_option_button(self, option: Option):
		self.add_item(OptionButton(option))

	async def update(self, replace_str: str):
		""" Updates Poll embed

			:param replace_str: String that will replace {timer} placeholder
		"""
		self.__embed = await create_poll_embed(self.__poll)
		self.__embed.description = self.__embed.description.replace("{timer}", replace_str)

		await self.__message.edit(embed=self.__embed, view=self)

	async def on_timer_update(self):
		await self.update(self.remaining_time)

	async def on_timer_elapsed(self):
		self.clear_items()
		await self.update('Poll is finished!')
		await self.__winner_callback(self.__poll)

	async def send(self, ctx: Context, embed: Embed):
		self.__message = await ctx.send(embed=embed, view=self)
		self.start_timer()


class OptionButton(Button):
	def __init__(self, option):
		super().__init__(style=ButtonStyle.gray, emoji=option.emoji)
		self.option = option

	async def callback(self, interaction: Interaction):
		""" Changes the counter based on user vote

		:param interaction: Button interaction
		"""
		poll = self.view.poll
		current_option = poll.selected_option_for(interaction.user)

		if current_option != self.option:
			poll.set_user_option(interaction.user, self.option)
			await self.view.update(self.view.remaining_time)

		if not interaction.is_expired():
			await interaction.response.defer()


class PollCog(Cog):
	# Current discord's view limitation is 25 buttons
	# An extra 7 more buttons/options still can be added
	MAX_OPTIONS: int = 18

	def __init__(self, bot: Grace):
		self.bot = bot

	def make_sequence(self, seq):
		""" Converts the object to an iterable
			:param seq: object
			:return: variable depending on its type
			:rtype: Sequence
		"""
		if seq is None:
			return ()
		if isinstance(seq, Sequence) and not isinstance(seq, str):
			return seq
		else:
			return seq,

	def message_check(self, channel=None, author=None, content=None, ignore_bot=True, lower=True) -> Callable[[Message], bool]:
		""" Functions ensures that the message was sent in the dm channel,
			and by the author himself.
			:param channel: 	Channel the message was sent in
			:param author: 		Message author
			:param content: 	Pattern matching parameter
			:param ignore_bot:  Whether the function should ignore the author being a bot or not
			:param lower: 		Whether the actual content is lowercase or not
			:return: Returns a function that checks the message
			:rtype: Callable
		"""
		channel = self.make_sequence(channel)
		author = self.make_sequence(author)
		content = self.make_sequence(content)

		if lower:
			content = tuple(c.lower() for c in content)

		def check(message: Message):
			""" Checks the message for validity
				:param message: Message that was read
				:rtype: bool
			"""
			if ignore_bot and message.author.bot:
				return False
			if channel and message.channel not in channel:
				return False
			if author and message.author not in author:
				return False
			actual_content = message.content.lower() if lower else message.content
			if content and actual_content not in content:
				return False
			return True
		return check

	async def display_winner(self, ctx: Context, poll: Poll):
		""" Displays the winner option of the poll
			:param ctx: Context of an interaction
			:param poll: A Poll
		"""
		winner: Option = poll.winner

		if winner:
			await ctx.channel.send(f'{winner.emoji} ***option has won!***')
		else:
			await ctx.channel.send('No one voted.')

	def get_emojis(self, options_count: int = 2):
		""" Retrieve emojis based on options count

		    :param options_count: Number of options chosen by the user
		"""
		if options_count == 2:
			return ['👍', '👎']

		return [
			'🟥', '🟧', '🟨', '🟩', '🟦', '🟪', '⬛', '⬜', '🟫',
			'🔴', '🟠', '🟡', '🟢', '🔵', '🟣', '⚫', '⚪', '🟤',
		][:options_count]

	async def get_options(self, ctx: Context, options_count: int = 2):
		""" Read options from user's dm channel

			:param ctx: Command context
			:param options_count: Number of options chosen by the user
		"""

		options = []
		emojis = self.get_emojis(options_count)

		options_embed = Embed(
			color=self.bot.default_color,
			title='POLL CREATION INFO',
			description=f'**Input {options_count} poll options.**\n To abort the poll type: **!abort**'
		)

		await ctx.author.send(embed=options_embed)

		for index in range(options_count):
			options_embed.description = f'**Input option {index + 1}.**'
			await ctx.author.send(embed=options_embed)

			try:
				message = await self.bot.wait_for(
					'message',
					check=self.message_check(ctx.author.dm_channel),
					timeout=360
				)
			except TimeoutError:
				return await ctx.author.send('**Waiting too long! Aborted!**')

			if message.content == '!abort':
				return await ctx.author.send('**Successfully aborted!**')

			options.append(Option(message.content, emojis[index]))
		return options

	@hybrid_group(name="poll", help="Poll commands")
	async def poll_group(self, ctx: Context):
		""" If no invoked subcommand was executed
			:param ctx: Command context
			:rtype: None
		"""
		if ctx.invoked_subcommand is None:
			await send_command_help(ctx)

	@poll_group.command(name='create', help='Create a poll')
	async def create_poll(self, ctx: Context, *, title: str, options_count: int = 2, poll_time_in_seconds: int = 120):
		""" Creates the poll
			:param ctx: 						Command context
			:param title: 						Title of the poll
			:param options_count: 				Number of options in the poll
			:param poll_time_in_seconds: 		Duration of the poll in seconds
		"""
		if options_count < 2 or options_count > self.MAX_OPTIONS:
			return await ctx.send(f'A poll needs between 2 and {self.MAX_OPTIONS} options.', ephemeral=True)

		await ctx.interaction.response.defer()
		options: List[Option] = await self.get_options(ctx, options_count)

		if not options:
			return

		await ctx.author.send(
			f'Great! The poll: {title} with {options_count} options created! On channel: {ctx.channel.name}')

		poll = Poll(options=options, title=title)
		poll_embed = await create_poll_embed(poll)
		view = PollView(poll, poll_embed, partial(self.display_winner, ctx), poll_time_in_seconds)

		for option in options:
			view.add_option_button(option)

		await view.send(ctx, poll_embed)


async def setup(bot):
	await bot.add_cog(PollCog(bot))
