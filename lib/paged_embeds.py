from typing import List, Any, Callable
from discord import Embed, Interaction
from discord.ui import View, Button
from emoji.core import emojize


class EmbedIterator:
    def __init__(self, collection):
        self._collection: List[Embed] = collection
        self._position: int = 0

    def next(self) -> Embed:
        if self.has_next():
            self._position += 1
        return self._collection[self._position]

    def previous(self) -> Embed:
        if self.has_previous():
            self._position -= 1
        return self._collection[self._position]

    def has_next(self) -> bool:
        return self._position + 1 < len(self._collection)

    def has_previous(self) -> bool:
        return self._position > 0


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
        super().__init__(timeout=None)
        self._embeds: EmbedIterator = EmbedIterator(embeds)
        self._arrow_button: List[EmbedButton] = [
            EmbedButton(self._embeds.previous, emoji=emojize(":left_arrow:"), disabled=True),
            EmbedButton(self._embeds.next, emoji=emojize(":right_arrow:"))
        ]

        self.add_item(self._arrow_button[0])
        self.add_item(self._arrow_button[1])

    async def after_button_callback(self):
        self._arrow_button[0].disabled = not self._embeds.has_previous()
        self._arrow_button[1].disabled = not self._embeds.has_next()
