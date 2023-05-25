from typing import List, Any, Callable, Optional
from discord import Embed, Interaction, Message
from discord.ext.commands import Context
from discord.ui import View, Button
from emoji.core import emojize
from lib.bidirectional_iterator import BidirectionalIterator


class EmbedButton(Button):
    def __init__(self, embed_callback: Callable, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._embed_callback: Callable = embed_callback

    async def callback(self, interaction: Interaction) -> Any:
        embed = self._embed_callback()
        await self.view.after_button_callback()

        return await interaction.response.edit_message(embed=embed, view=self.view)


class PagedEmbedView(View):
    def __init__(self, embeds: List[Embed]):
        super().__init__()

        self.__message: Optional[Message] = None
        self.__embeds: BidirectionalIterator[Embed] = BidirectionalIterator(embeds)
        self.__arrow_button: List[EmbedButton] = [
            EmbedButton(self.__embeds.previous, emoji=emojize(":left_arrow:"), disabled=True),
            EmbedButton(self.__embeds.next, emoji=emojize(":right_arrow:"), disabled=True)
        ]

        self.add_item(self.previous_arrow)
        self.add_item(self.next_arrow)

        self.refresh_arrows()

    @property
    def next_arrow(self) -> EmbedButton:
        return self.__arrow_button[1]

    @property
    def previous_arrow(self) -> EmbedButton:
        return self.__arrow_button[0]

    def add_embed(self, embed: Embed):
        self.__embeds.add(embed)
        self.refresh_arrows()

    def refresh_arrows(self):
        self.previous_arrow.disabled = not self.__embeds.has_previous()
        self.next_arrow.disabled = not self.__embeds.has_next()

    async def after_button_callback(self):
        self.refresh_arrows()

    async def on_timeout(self):
        self.remove_item(self.previous_arrow)
        self.remove_item(self.next_arrow)

        await self.__message.edit(embed=self.__embeds.current, view=self)

    async def send(self, ctx: Context, ephemeral: bool = True):
        self.__message = await ctx.send(embed=self.__embeds.current, view=self, ephemeral=ephemeral)