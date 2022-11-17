from typing import Callable
from discord.ext.commands import Cog, Context, hybrid_command, hybrid_group
from bot.extensions.command_error_handler import send_command_help
from collections.abc import Sequence
from discord import Embed
from discord.ui import Button, View
import discord
import random
import asyncio


# Problem: The modal doesn't allow more than 5 input fields (In the poll I assume there could be more)
# Problem: Cannot make the bot output one modal after another (I can send 1 modal but after it says interaction expired or something).
# When I try using webhooks it gives me 'Unknown Webhook' error
# TODO(LIMITATION): Try to find a workaround with models. Or just accept user input: https://stackoverflow.com/questions/64949395/how-can-i-make-my-discord-bot-respond-with-a-follow-up-message


#class TitleBuilder(ui.Modal):
# 	def __init__(self):
# 		super().__init__(title='Title')
# 		self.input = ui.TextInput(label='Text')
# 		self.add_item(self.input)

# 	async def on_submit(self, interaction: discord.Interaction):
# 		await interaction.response.send_message(f'Text: {self.input}', ephemeral=True)

# class OptionBuilder(ui.Modal):
# 	def __init__(self, option: int):
# 		super().__init__(title=f'Option {option}')
# 		self.option = ui.TextInput(label=f"Option {option}")
# 		self.add_item(self.option)

# 	async def on_submit(self, interaction: discord.Interaction):
# 		await interaction.response.send_message(f'Text: {self.option}', ephemeral=True)

class PollView(View):
	def __init__(self, emojis: list[str], possible_emojis_size: int, ref_embed: Embed) -> None:
		super().__init__()
		self.buttons = []
		for emoji_index in range(possible_emojis_size):
			button = VoteButton(emojis[emoji_index])
			button.set_embed_reference(ref_embed)
			self.add_item(button)
			self.buttons.append(button)

	def disable_buttons(self) -> None:
		for button in self.buttons:
			button.disabled = True


class PollEmbed(Embed):
	def __init__(self, *, options: list[str], emojis: list[str], counter: dict, title: str) -> None:
		super().__init__()
		# User: vote_emoji
		self._voted_users = {}
		self._poll_options = options
		self._poll_emojis = emojis
		self._poll_counter = counter
		self._poll_title = title
		self._timer_label = None

	def increment_counter(self, emoji: str) -> None:
		self._poll_counter[emoji] += 1

	def decrement_counter(self, emoji: str) -> None:
		self._poll_counter[emoji] -= 1

	def set_user(self, user: discord.Member, emoji: str) -> None:
		self._voted_users[user] = emoji

	def get_user_emoji(self, user: discord.Member) -> str:
		return self._voted_users[user]

	def user_voted(self, user: discord.Member) -> bool:
		if user in self._voted_users:
			return True
		return False

	def set_timer_label(self, label: str) -> None:
		self._timer_label = label

	async def get_and_print_winner(self, ctx: Context) -> None:
		highest = 0
		win_emoji = ''
		for emoji, count in self._poll_counter.items():
			if count > highest:
				highest = count
				win_emoji = emoji

		if highest > 0 and win_emoji:
			await ctx.channel.send(f'{win_emoji} ***option has won!***')
		else:
			await ctx.channel.send('No one voted.')



	def build(self) -> None:
		# Set the embed title
		self.title = self._poll_title
		
		# Generate the description
		main_text = ''
		if self._timer_label:
			main_text += (self._timer_label + '\n\n')

		for emoji_index, option in enumerate(self._poll_options):
			# Check if the number of emojis needed is not out of boundaries
			if emoji_index < len(self._poll_emojis):
				emoji = self._poll_emojis[emoji_index]
			else:
				break
			main_text += (emoji + ' **' + option + '**: ' + str(self._poll_counter[emoji]) + '\n\n')

		self.description = main_text

class VoteButton(Button):
	def __init__(self, emoji) -> None:
		super().__init__(style=discord.ButtonStyle.gray, emoji=emoji)

	def set_embed_reference(self, embed: PollEmbed) -> None:
		self._embed = embed


	async def callback(self, interaction: discord.Interaction) -> None:
		if self._embed is None:
			raise ValueError('Update embed function or/and Counter reference are not set.')
		# TODO: Catch the unknown interaction error and send a message that user is clicking too fast.
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

'''
	PollEmbed:
		counter = {}
	ButtonsView:
		VoteButton -> (emoji)
		VoteButton.set_embed_ref(PollEmbed)
		VoteButton.callback() -> counter[emoji] += 1; embed_update();
'''
class Timer:
	def __init__(self, msg: discord.Message, seconds: int, embed: PollEmbed, view: PollView) -> None:
		self._seconds = seconds
		self._embed = embed
		self._view = view
		self._msg = msg

	async def start(self) -> None:
		while self._seconds >= 0:
			await self.timer_info_update()
			await asyncio.sleep(1)
			self._seconds -= 1

		self._view.disable_buttons()
		await self._msg.edit(embed=self._embed, view=self._view)


	async def timer_info_update(self) -> None:
		if self._seconds // 60 >= 10:
			if self._seconds % 60 >= 10:
				self._embed.set_timer_label(f'**{self._seconds // 60}:{self._seconds % 60}**')
			else:
				self._embed.set_timer_label(f'**{self._seconds // 60}:0{self._seconds % 60}**')
		else:
			if self._seconds % 60 >= 10:
				self._embed.set_timer_label(f'**0{self._seconds // 60}:{self._seconds % 60}**')
			else:
				self._embed.set_timer_label(f'**0{self._seconds // 60}:0{self._seconds % 60}**')

		self._embed.build()
		await self._msg.edit(embed=self._embed)


# Limitation: It's only possible to run 1 poll at a time. Well you can run 2 or more but it's not gonna be asynchronous
# Suggestion: Probably use (if exists) discord's built-in threads, to separate the processes.
class PollCog(Cog):
	def __init__(self, bot: discord.ext.commands.Bot) -> None:
		self.bot = bot

	def make_sequence(self, seq):
	    if seq is None:
	        return ()
	    if isinstance(seq, Sequence) and not isinstance(seq, str):
	        return seq
	    else:
	        return (seq,)    

	def message_check(self, channel=None, author=None, content=None, ignore_bot=True, lower=True) -> Callable[[discord.Message], bool]:
	    channel = self.make_sequence(channel)
	    author = self.make_sequence(author)
	    content = self.make_sequence(content)
	    if lower:
	        content = tuple(c.lower() for c in content)
	    def check(message: discord.Message):
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

	@hybrid_group(name="poll", help="Poll commands")
	async def poll_group(self, ctx) -> None:
		if ctx.invoked_subcommand is None:
		    await send_command_help(ctx)

	@poll_group.command(name='create', help='Create a poll')
	async def vote(self, ctx: Context, *, title: str, options_count: int = 2, poll_time: int = 120) -> None:
		if options_count < 2:
			await ctx.interaction.response.send_message('Only 2 or more options is allowed.', ephemeral=True)
			return
		cancel_keywords = ['!abort']

		# if not title:
		# 	# Create title embed
		# 	title_embed = Embed(
		# 		color=self.bot.default_color,
		# 		title='POLL CREATION INFO',
		# 		description='**Input poll title**'
		# 	)
		# 	# Send a DM to the command executor
		# 	await ctx.author.send(embed=title_embed)

		# 	# TODO: Think if input title can be invalid
		# 	title = await self.bot.wait_for('message', check=self.message_check(ctx.author.dm_channel))

		# 	# Check if user cancelled the poll
		# 	if title.content.lower().strip() in cancel_keywords:
		# 		await ctx.interaction.response.send_message('Aborted', ephemeral=True)
		# 		return

		options_embed = Embed(
			color=self.bot.default_color,
			title='POLL CREATION INFO',
			description=f'**Input {options_count} poll options.**\n To abort the poll type: **!abort**'
		)

		await ctx.author.send(embed=options_embed)
		options = []

		# Read the input from dm and save it in options list
		for index in range(options_count):
			option_embed = Embed(
				color=self.bot.default_color,
				title='POLL CREATION INFO',
				description=f'**Input option {index + 1}.**'
			)
			await ctx.author.send(embed=option_embed)
			# Wait for input
			option = await self.bot.wait_for('message', check=self.message_check(ctx.author.dm_channel))
			# Check if user cancelled the poll
			if option.content in cancel_keywords:
				await ctx.author.send('**Successfully aborted!**')
				return
			options.append(option.content)

		# Send a success message
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

		# Create poll embed
		poll_embed = PollEmbed(
			options=options, 
			emojis=emojis, 
			counter=counter, 
			title=title
		)
		# Create poll view
		view = PollView(emojis, allowed_emojis_size, poll_embed)
		# build/initialize embed
		poll_embed.build()

		# Send a poll message
		poll = await ctx.channel.send(embed=poll_embed, view=view)
		# Create timer
		timer = Timer(poll, poll_time, poll_embed, view)
		await timer.start()
		
		# Output the winner option
		await poll_embed.get_and_print_winner(ctx)




async def setup(bot):
	await bot.add_cog(PollCog(bot))
