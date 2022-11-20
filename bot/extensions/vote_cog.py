from typing import Callable
from bot.extensions.command_error_handler import send_command_help
from collections.abc import Sequence
from discord.ext.commands import Bot, Cog, Context, hybrid_command, hybrid_group
from discord import Embed, Member, ButtonStyle, Interaction, Message
from discord.ui import Button, View
from asyncio import sleep as async_sleep
from asyncio import TimeoutError


class PollView(View):
	def __init__(self, emojis: list[str], possible_emojis_size: int, ref_embed: Embed) -> None:
		super().__init__()
		self._buttons = []
		self._possible_emojis_size = possible_emojis_size
		self._emojis = emojis
		self._embed = ref_embed
		self.create_buttons()

	def create_buttons(self) -> None:
		""" Create/intitalize the buttons of the View"""
		for emoji_index in range(self._possible_emojis_size):
			button = VoteButton(self._emojis[emoji_index])
			button.set_embed_reference(self._embed)
			self.add_item(button)
			self._buttons.append(button)

	def disable_buttons(self) -> None:
		for button in self._buttons:
			button.disabled = True


class PollEmbed(Embed):
	def __init__(self, *, options: list[str], emojis: list[str], counter: dict, title: str) -> None:
		super().__init__()
		self._voted_users = {}
		self._poll_options = options
		self._poll_emojis = emojis
		self._poll_counter = counter
		self._poll_title = title
		self._timer_label = None

	def increment_counter(self, emoji: str) -> None:
		""" Increment emoji counter (when someone voted)"""
		self._poll_counter[emoji] += 1

	def decrement_counter(self, emoji: str) -> None:
		""" Decrement emoji counter (when someone changed their vote)"""
		self._poll_counter[emoji] -= 1

	def set_user(self, user: Member, emoji: str) -> None:
		""" Set user's vote choice """
		self._voted_users[user] = emoji

	def get_user_emoji(self, user: Member) -> str:
		""" Get user's voted option """
		return self._voted_users[user]

	def user_voted(self, user: Member) -> bool:
		if user in self._voted_users:
			return True
		return False

	def set_timer_label(self, label: str) -> None:
		self._timer_label = label

	def finish(self) -> None:
		self._timer_label = '**Poll finished!**'
		self.build()

	@property
	def counter(self):
		return self._poll_counter

	def build(self) -> None:
		""" Builds/initializes embed's properties: title, description """

		self.title = self._poll_title
		
		# Generate the description
		main_text = ''
		if self._timer_label:
			main_text += self._timer_label + '\n\n'

		for emoji_index, option in enumerate(self._poll_options):
			if emoji_index < len(self._poll_emojis):
				emoji = self._poll_emojis[emoji_index]
			else:
				break
			main_text += (emoji + ' **' + option + '**: ' + str(self._poll_counter[emoji]) + '\n\n')

		self.description = main_text


class VoteButton(Button):
	def __init__(self, emoji) -> None:
		super().__init__(style=ButtonStyle.gray, emoji=emoji)

	def set_embed_reference(self, embed: PollEmbed) -> None:
		self._embed = embed

	async def callback(self, interaction: Interaction) -> None:
		""" When button was clicked.
			Manipulates the embed counter depending on user interaction """
		if self._embed is None:
			raise ValueError('Embed is not set')

		if self._embed.user_voted(interaction.user):
			user_emoji = self._embed.get_user_emoji(interaction.user)
			if self.emoji.name != user_emoji:
				self._embed.decrement_counter(user_emoji)
				self._embed.increment_counter(self.emoji.name)
				self._embed.set_user(interaction.user, self.emoji.name)
				self._embed.build()
				await interaction.message.edit(embed=self._embed)
		else:
			self._embed.increment_counter(self.emoji.name)
			self._embed.set_user(interaction.user, self.emoji.name)
			self._embed.build()
			await interaction.message.edit(embed=self._embed)
		await interaction.response.defer()


class Timer:
	def __init__(self, msg: Message, seconds: int, embed: PollEmbed, view: PollView) -> None:
		self._seconds = seconds
		self._embed = embed
		self._view = view
		self._msg = msg

	async def start(self) -> None:
		""" Starts and executes the timer """
		while self._seconds >= 0:
			await self.timer_info_update()
			await async_sleep(1)
			self._seconds -= 1

		self._view.disable_buttons()	

	def dozen_seconds(self) -> bool:
		""" Checks if there is more than 10 seconds"""
		if self._seconds % 60 >= 10:
			return True
		return False

	def dozen_minutes(self) -> bool:
		""" Checks if there is more than 10 minutes"""
		if self._seconds // 60 >= 10:
			return True
		return False

	def set_timer_label(self) -> None:
		dozen_minutes = self.dozen_minutes()
		dozen_seconds = self.dozen_seconds()
		self._embed.set_timer_label(f'**{0 if not dozen_minutes else ""}{self._seconds // 60}:{0 if not dozen_seconds else ""}{self._seconds % 60}**')

	async def timer_info_update(self) -> None:
		""" Updates the embed's timer label """
		self.set_timer_label()
		self._embed.build()
		await self._msg.edit(embed=self._embed)


class PollCog(Cog):
	def __init__(self, bot: Bot) -> None:
		self.bot = bot

	def make_sequence(self, seq):
		""" Returns the variable depending on it's type """
		if seq is None:
			return ()
		if isinstance(seq, Sequence) and not isinstance(seq, str):
			return seq
		else:
			return (seq,)

	def message_check(self, channel=None, author=None, content=None, ignore_bot=True, lower=True) -> Callable[[Message], bool]:
		""" Functions ensures that the message was sent in the dm channel,
			and by the author himself.
		"""
		channel = self.make_sequence(channel)
		author = self.make_sequence(author)
		content = self.make_sequence(content)
		if lower:
			content = tuple(c.lower() for c in content)
		def check(message: Message):
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

	async def get_and_print_winner(self, ctx: Context) -> None:
		""" Calculates the highest voted option and sends the victory message """
		highest = 0
		win_emoji = ''
		for emoji, count in self.poll_embed.counter.items():
			if count > highest:
				highest = count
				win_emoji = emoji

		if highest > 0 and win_emoji:
			await ctx.channel.send(f'{win_emoji} ***option has won!***')
		else:
			await ctx.channel.send('No one voted.')

	@hybrid_group(name="poll", help="Poll commands")
	async def poll_group(self, ctx) -> None:
		""" If no invoked subcommand was executed """
		if ctx.invoked_subcommand is None:
			await send_command_help(ctx)

	@poll_group.command(name='create', help='Create a poll')
	async def vote(self, ctx: Context, *, title: str, options_count: int = 2, poll_time: int = 120) -> None:
		""" Constructs the vote embed """
		if options_count < 2:
			await ctx.interaction.response.send_message('Only 2 or more options is allowed.', ephemeral=True)
			return

		cancel_keywords = ['!abort']

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
				await ctx.author.send('**Waiting too long! Aborted!**')
				return

			if option.content in cancel_keywords:
				await ctx.author.send('**Successfully aborted!**')
				return
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
		# Votes counter according to vote emoji chosen
		counter = {}
		# allowed size of counter array, needed if there is more than 18 options.
		allowed_emojis_size = len(options) if len(options) < len(emojis) else len(emojis)
		for emoji_index in range(allowed_emojis_size):
			counter[emojis[emoji_index]] = 0


		self.poll_embed = PollEmbed(
			options=options, 
			emojis=emojis, 
			counter=counter, 
			title=title
		)

		self.view = PollView(emojis, allowed_emojis_size, self.poll_embed)
		self.poll_embed.build()


		poll = await ctx.channel.send(embed=self.poll_embed, view=self.view)

		timer = Timer(poll, poll_time, self.poll_embed, self.view)
		await timer.start()

		self.poll_embed.finish()
		await poll.edit(embed=self.poll_embed, view=self.view)
		
		# Output the winner option
		await self.get_and_print_winner(ctx)


async def setup(bot):
	""" Adds the PollCog to the bot """ 
	await bot.add_cog(PollCog(bot))
