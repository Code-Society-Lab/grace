from discord.ext.commands import Cog, hybrid_command
from discord.ui import View
from discord import ButtonStyle, ui
from urllib.request import urlopen
from urllib.parse import quote_plus
from json import loads
from discord import Embed


def search_results(search: str):
    """Return search results from Wikipedia for the given search query.
    
    :param search: The search query to be used to search Wikipedia.
    :type search: str

    :return: A list of search results.
    :rtype: list
    """
    url_encode = quote_plus(search)
    url = f"https://en.wikipedia.org/w/api.php?action=opensearch&format=json&limit=3&namespace=0&search={url_encode}"
    with urlopen(url) as url:
        return loads(url.read())


class Buttons(View):
    def __init__(self, search, result):
        super().__init__()
        self.search = search
        self.result = result

    async def wiki_result(self, interaction: Interaction, _, index: int):
        """Send the selected search result to the user.

        :param interaction: The interaction object representing the user's interaction with the bot.
        :type interaction: Interaction
        :param index: The index of the search result to be sent to the user.
        :type index: int
        """
        if len(self.result[3]) >= index:
            await interaction.response.send_message("{mention} requested:\n {request}".format(
                mention=interaction.user.mention,
                request=self.result[3][index-1]
            ))
            self.stop()
        else:
            await interaction.response.send_message("Invalid choice.", ephemeral=True)

    @ui.button(label='1', style=ButtonStyle.primary)
    async def first_wiki_result(self, interaction, button):
        await self.wiki_result(interaction, button, 1)

    @ui.button(label='2', style=ButtonStyle.primary)
    async def second_wiki_result(self, interaction, button):
        await self.wiki_result(interaction, button, 2)

    @ui.button(label='3', style=ButtonStyle.primary)
    async def third_wiki_result(self, interaction, button):
        await self.wiki_result(interaction, button, 3)


class Wikipedia(Cog, name="Wikipedia", description="Search on Wikipedia."):
    def __init__(self, bot):
        self.bot = bot

    @hybrid_command(name="wiki", description="Searches and displays the first 3 results from Wikipedia.")
    async def wiki(self, ctx, *, search: str):
        """Search Wikipedia and display the first 3 search results to the user.

        :param ctx: The context in which the command was invoked.
        :type ctx: Context
        :param search: The search query to be used to search Wikipedia.
        :type search: str
        """
        result = search_results(search)
        view = Buttons(search, result)

        if len(result[1]) == 0:
            await ctx.interaction.response.send_message("No result found.", ephemeral=True)
        else:
            result_view = ""
            search_count = 1
            for result in result[1]:
                result_view += f"{str(search_count)}: {result}\n"
                search_count += 1

            embed = Embed(
                color=0x2376ff,
                title=f"Top 3 Wikipedia Search",
                description=result_view,
            )
            await ctx.send(embed=embed, view=view, ephemeral=True)


async def setup(bot):
    await bot.add_cog(Wikipedia(bot))
