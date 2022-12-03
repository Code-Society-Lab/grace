from typing import Callable, Optional, Any
from bot.extensions.command_error_handler import send_command_help
from collections.abc import Sequence
from discord.ext.commands import Bot, Cog, Context, hybrid_group
from discord import Embed, ButtonStyle, Interaction, Message
from discord.ui import Button
from asyncio import TimeoutError
from lib.timed_view import TimedView
from bot.classes.poll import PollModel


class PollEmbed(Embed):
	def __init__(self, model: PollModel) -> None:
		super().__init__()
		self._model: PollModel = model

	@property
	def model(self):
		return self._model

	def build(self) -> None:
		self.title = self.model.title

		main_text = ''
		if self.model.timer_label is not None:
			main_text += self.model.timer_label + '\n\n'

		for emoji_index, option in enumerate(self.model.options):
			if emoji_index < len(self.model.emojis):
				emoji = self.model.emojis[emoji_index]
			else:
				break
			main_text += (emoji + ' **' + option + '**: ' + str(self.model.counter[emoji]) + '\n\n')

		self.description = main_text


class PollView(TimedView):
	def __init__(
			self,
			embed: PollEmbed,
			model: PollModel,
			ctx: Context,
			win_callback: Callable,
			seconds: int
	):
		super().__init__(seconds)
		self._embed: PollEmbed = embed
		self._model: PollModel = model
		self._ctx: Context = ctx
		self._win_callback: Callable = win_callback
		self._seconds: int = seconds
		self._msg: Optional[Message] = None
		self.create_buttons()

	def create_buttons(self):
		for emoji_index in range(self._model.allowed_emoji_size):
			button = VoteButton(self._embed, self._model.emojis[emoji_index])
			self.add_item(button)

	def set_message(self, msg: Message):
		self._msg = msg

	def set_timer_label(self):
		self._embed.model.timer_label = self.remaining_time

	async def timer_info_update(self):
		self.set_timer_label()
		self._embed.build()
		await self._msg.edit(embed=self._embed)

	async def on_timer_update(self) -> Any:
		await self.timer_info_update()
	async def on_timer_elapsed(self):
		self._embed.model.timer_label = "Poll is finished"
		self._embed.build()
		self.clear_items()
		await self._msg.edit(embed=self._embed, view=self)
		await self._win_callback(self._ctx, self._model)


class VoteButton(Button):
	def __init__(self, embed: PollEmbed, emoji):
		super().__init__(style=ButtonStyle.gray, emoji=emoji)
		self._embed = embed

	async def callback(self, interaction: Interaction):
		""" Manipulates the embed counter depending on user interaction
			:param interaction: Button interaction
		"""
		if self._embed.model.user_has_voted(interaction.user):
			user_emoji = self._embed.model.get_user_emoji(interaction.user)
			if self.emoji.name != user_emoji:
				self._embed.model.decrement_counter(user_emoji)
				self._embed.model.increment_counter(self.emoji.name)
				self._embed.model.set_user(interaction.user, self.emoji.name)
				self._embed.build()
				await interaction.message.edit(embed=self._embed)
		else:
			self._embed.model.increment_counter(self.emoji.name)
			self._embed.model.set_user(interaction.user, self.emoji.name)
			self._embed.build()
			await interaction.message.edit(embed=self._embed)
		await interaction.response.defer()


class PollCog(Cog):
	def __init__(self, bot: Bot):
		self.bot = bot

	def make_sequence(self, seq):
		""" Converts the object to an iterable
			:param seq: object
			:return: variable depending on it's type
			:rtype: Sequence
		"""
		print(seq, type(seq))
		if seq is None:
			return ()
		if isinstance(seq, Sequence) and not isinstance(seq, str):
			return seq
		else:
			return (seq,)

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

	async def get_and_print_winner(self, ctx: Context, model: PollModel):
		""" Calculates the highest voted option and sends the victory message
			:param ctx: Context of an interaction
			:param model: Poll model
		"""
		highest = 0
		win_emoji = ''
		for emoji, count in model.counter.items():
			if count > highest:
				highest = count
				win_emoji = emoji

		if highest > 0 and win_emoji:
			await ctx.channel.send(f'{win_emoji} ***option has won!***')
		else:
			await ctx.channel.send('No one voted.')

	@hybrid_group(name="poll", help="Poll commands")
	async def poll_group(self, ctx: Context):
		""" If no invoked subcommand was executed
			:param ctx: Context of an interaction
			:rtype: None
		"""
		if ctx.invoked_subcommand is None:
			await send_command_help(ctx)

	@poll_group.command(name='create', help='Create a poll')
	async def vote(self, ctx: Context, *, title: str, options_count: int = 2, poll_time: int = 120):
		""" Constructs the poll embed
			:param ctx: 			Context of an interaction
			:param title: 			Title of the poll
			:param options_count: 	Number of options in the poll
			:param poll_time: 		Duration of the poll
		"""
		if options_count < 2:
			return await ctx.interaction.response.send_message('Only 2 or more options is allowed.', ephemeral=True)

		options_embed = Embed(
			color=self.bot.default_color,
			title='POLL CREATION INFO',
			description=f'**Input {options_count} poll options.**\n To abort the poll type: **!abort**'
		)

		await ctx.author.send(embed=options_embed)
		options = []

		for index in range(options_count):
			option_embed = Embed(
				color=self.bot.default_color,
				title='POLL CREATION INFO',
				description=f'**Input option {index + 1}.**'
			)
			await ctx.author.send(embed=option_embed)
			try:
				option = await self.bot.wait_for('message', check=self.message_check(ctx.author.dm_channel), timeout=360)
			except TimeoutError:
				return await ctx.author.send('**Waiting too long! Aborted!**')

			if option.content == '!abort':
				return await ctx.author.send('**Successfully aborted!**')

			options.append(option.content)

		await ctx.author.send(f'Great! The poll: {title} with {len(options)} options created! On channel: {ctx.channel.name}')
		if options_count == 2:
			emojis = [
				'👍', '👎'
			]
		else:
			emojis = [
				'🟥', '🟧', '🟨', '🟩', '🟦', '🟪', '⬛', '⬜', '🟫',
				'🔴', '🟠', '🟡', '🟢', '🔵', '🟣', '⚫', '⚪', '🟤',
			]
		counter = {}
		# allowed size of counter array, needed if there is more than 18 options.
		allowed_emojis_size = len(options) if len(options) < len(emojis) else len(emojis)
		for emoji_index in range(allowed_emojis_size):
			counter[emojis[emoji_index]] = 0

		model = PollModel(
			options=options,
			emojis=emojis,
			allowed_emoji_size=allowed_emojis_size,
			counter=counter,
			title=title
		)

		poll_embed = PollEmbed(model)
		poll_embed.build()

		view = PollView(
			embed=poll_embed,
			model=model,
			ctx=ctx,
			win_callback=self.get_and_print_winner,
			seconds=poll_time
		)

		poll = await ctx.channel.send(embed=poll_embed, view=view)

		view.set_message(poll)

		view.start_timer()


async def setup(bot):
	""" Adds the PollCog to the bot """
	await bot.add_cog(PollCog(bot))