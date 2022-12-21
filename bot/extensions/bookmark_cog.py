from typing import List
from discord import Embed, Message, Interaction, File
from discord.app_commands import ContextMenu
from discord.ext.commands import Cog
from bot.extensions.command_error_handler import send_command_help
from bot.grace import Grace
from datetime import timedelta


class BookmarkCog(Cog):
	def __init__(self, bot: Grace) -> None:
		self.bot: Grace = bot

		save_message_ctx_menu = ContextMenu(
			name='Save Message',
			callback=self.save_message
		)

		self.bot.tree.add_command(save_message_ctx_menu)
	
	async def fetch_files(self, message: Message) -> List[File]:
		"""Fetch files from the message attachments
		
		:param message: Message to fetch files from
		"""
		files = []
		for attachment in message.attachments:
			files.append(await attachment.to_file())
		return files

	async def save_message(self, interaction: Interaction, message: Message) -> None:
		"""Saves the message
		
		:param interaction: ContextMenu command interaction
		:param message: Message of the interaction
		"""
		date: int = (message.created_at + timedelta(hours=1)).strftime('%s')
		files = await self.fetch_files(message)
		save_embed: Embed = Embed(
			title='Save Info',
			description=f'Message sent by: **{message.author}**\n'
						f'Sent at: **<t:{date}>**\n'
						f':arrow_down:',
			color=self.bot.default_color
		)
		await interaction.user.send(embed=save_embed)
		await interaction.user.send(message.content, embeds=message.embeds, files=files)
		await interaction.response.send_message("Message successfully saved.", ephemeral=True)


async def setup(bot: Grace) -> None:
	await bot.add_cog(BookmarkCog(bot))