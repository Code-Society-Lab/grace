from typing import List
from discord import Embed, Message, Interaction, File
from discord.app_commands import ContextMenu
from discord.ext.commands import Cog
from bot.grace import Grace


class BookmarkCog(Cog):
	def __init__(self, bot: Grace) -> None:
		self.bot: Grace = bot

		save_message_ctx_menu: ContextMenu = ContextMenu(
			name='Save Message',
			callback=self.save_message
		)

		self.bot.tree.add_command(save_message_ctx_menu)

	async def get_message_files(self, message: Message) -> List[File]:
		"""Fetch files from the message attachments
		
		:param message: Message to fetch files from
		:type message: Message

		:return: List of files
		:rtype: List[File]
		"""
		return list(map(lambda attachment: attachment.to_file(), message.attachments))

	async def save_message(self, interaction: Interaction, message: Message) -> None:
		"""Saves the message
		
		:param interaction: ContextMenu command interaction
		:type interaction: Interaction
		:param message: Message of the interaction
		:type message: Message
		"""
		sent_at: int = int(message.created_at.timestamp())
		files: List[File] = await self.get_message_files(message)

		save_embed: Embed = Embed(
			title='Bookmark Info',
			color=self.bot.default_color
		)

		save_embed.add_field(name="Sent By", value=message.author, inline=False)
		save_embed.add_field(name="Sent At", value=f'<t:{sent_at}>', inline=False)
		save_embed.add_field(name="Original Message", value=f'[Jump]({message.jump_url})', inline=False)

		await interaction.user.send(embed=save_embed)
		await interaction.user.send(message.content, embeds=message.embeds, files=files)
		await interaction.response.send_message("Message successfully saved.", ephemeral=True)


async def setup(bot: Grace) -> None:
	await bot.add_cog(BookmarkCog(bot))
