from functools import partial
from typing import Callable, Optional, List
from bot.extensions.command_error_handler import send_command_help
from discord.ext.commands import Cog, Context, hybrid_group
from discord import Embed, ButtonStyle, Interaction, Message
from discord.ui import Button
from asyncio import TimeoutError
from bot.grace import Grace
from lib.timed_view import TimedView
from bot.classes.poll import Poll, Option


async def create_poll_embed(poll: Poll) -> Embed:
	"""Returns a newly created poll embed

	:param poll: A Poll
	:type poll: Poll

	:returns: The created embed for the poll
	:rtype: Embed
	"""
	description: str = "{header}\n\n"

	for option in poll.options:
		description += f"{option.emoji} **{option.title}**: {poll.counter[option]}\n\n"

	return Embed(title=poll.title, description=description)


class PollView(TimedView):
	def __init__(self, poll: Poll, embed: Embed, winner_callback: Callable, seconds: int):
		super().__init__(seconds=seconds)

		self.__poll: Poll = poll
		self.__embed: Embed = embed
		self.__winner_callback: Callable = winner_callback
		self.__message: Optional[Message] = None

	@property
	def poll(self) -> Poll:
		return self.__poll

	@property
	def message(self) -> Optional[Message]:
		return self.__message

	@message.setter
	def message(self, message):
		if self.__message is None:
			self.__message = message

	def add_option_button(self, option: Option):
		self.add_item(OptionButton(option))

	def set_embed_header(self, content: str):
		if self.__embed.description:
			self.__embed.description = self.__embed.description.replace("{header}", content)

	async def update(self):
		self.__embed = await create_poll_embed(self.__poll)

		if self.has_time_elapsed():
			self.set_embed_header("Poll has ended!")
		else:
			self.set_embed_header(self.remaining_time)

		await self.__message.edit(embed=self.__embed, view=self)

	async def on_timer_update(self):
		await self.update()

	async def on_timer_elapsed(self):
		self.clear_items()

		await self.update()
		await self.__winner_callback(self.__poll)

	async def send(self, ctx: Context, embed: Embed):
		self.__message = await ctx.send(embed=embed, view=self)
		self.start_timer()


class OptionButton(Button):
	def __init__(self, option):
		super().__init__(style=ButtonStyle.gray, emoji=option.emoji)
		self.__option: Option = option

	async def callback(self, interaction: Interaction) -> None:
		if not self.view:
			return None

		poll: Poll = self.view.poll
		current_option: Option = poll.selected_option_for(interaction.user)

		if current_option != self.__option:
			poll.set_user_option(interaction.user, self.__option)
			await self.view.update(self.view.remaining_time)

		if not interaction.is_expired():
			await interaction.response.defer()


class PollCog(Cog):
	# Current discord's view limitation is 25 buttons
	# An extra 7 more buttons/options still can be added
	MAX_OPTIONS: int = 18

	def __init__(self, bot: Grace):
		self.bot = bot

	async def display_winner(self, ctx: Context, poll: Poll):
		winner: Optional[Option] = poll.winner

		if winner:
			await ctx.channel.send(f'{winner.emoji} ***option has won!***')
		else:
			await ctx.channel.send('No one voted.')

	def get_emojis(self, options_count: int = 2) -> List[str]:
		if options_count == 2:
			return ['👍', '👎']

		return [
			'🟥', '🟧', '🟨', '🟩', '🟦', '🟪', '⬛', '⬜', '🟫',
			'🔴', '🟠', '🟡', '🟢', '🔵', '🟣', '⚫', '⚪', '🟤',
		][:options_count]

	async def get_options(self, ctx: Context, options_count: int = 2) -> Optional[List[Option]]:
		def check(m: Message) -> bool:
			return ctx.author == m.author

		options: List[Option] = []
		emojis: List[str] = self.get_emojis(options_count)

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
				message = await self.bot.wait_for('message', check=check, timeout=360)
			except TimeoutError:
				await ctx.author.send('**Waiting too long! Aborted!**')
				return None

			if message.content == '!abort':
				await ctx.author.send('**Successfully aborted!**')
				return None

			options.append(Option(message.content, emojis[index]))
		return options

	@hybrid_group(name="poll", help="Poll commands")
	async def poll_group(self, ctx: Context):
		if ctx.invoked_subcommand is None:
			await send_command_help(ctx)

	@poll_group.command(name='create', help='Create a poll')
	async def create_poll(self, ctx: Context, *, title: str, options_count: int = 2, poll_time_in_seconds: int = 120):
		if options_count < 2 or options_count > self.MAX_OPTIONS:
			return await ctx.send(f'A poll needs between 2 and {self.MAX_OPTIONS} options.', ephemeral=True)

		await ctx.interaction.response.defer()
		options: Optional[List[Option]] = await self.get_options(ctx, options_count)

		if not options:
			return await ctx.reply("Aborted!")

		await ctx.author.send(
			f'Great! The poll: {title} with {options_count} options created! On channel: {ctx.channel.name}')

		poll: Poll = Poll(options=options, title=title)
		poll_embed: Embed = await create_poll_embed(poll)
		view: PollView = PollView(poll, poll_embed, partial(self.display_winner, ctx), poll_time_in_seconds)

		for option in options:
			view.add_option_button(option)

		await view.send(ctx, poll_embed)


async def setup(bot):
	await bot.add_cog(PollCog(bot))
