from typing import List, Any
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
        return self._position < len(self._collection)

    def has_previous(self) -> bool:
        return self._position > 0


class EmbedButton(Button):
    def __init__(self, embed: Embed, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.embed: Embed = embed

    async def callback(self, interaction: Interaction) -> Any:
        return await interaction.response.edit_message(embed=self.embed, view=self.view)


class PagedEmbedView(View):
    def __init__(self, embeds: List[Embed]):
        super().__init__()
        self._embeds: EmbedIterator = EmbedIterator(embeds)

        self.add_item(EmbedButton(self._embeds.previous(), emoji=emojize(":left_arrow:")))
        self.add_item(EmbedButton(self._embeds.next(), emoji=emojize(":right_arrow:")))
