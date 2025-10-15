from math import ceil
from typing import Iterable, List

from discord import Color, Embed
from discord.ui import Button
from emoji import emojize
from github import Organization, Repository

from bot.services.github_service import GithubService


def available_project_names() -> Iterable[str]:
    organization: Organization = GithubService().get_code_society_lab()
    return map(lambda r: r.name, organization.get_repos())


def create_contributors_embeds(repository: Repository) -> List[Embed]:
    """Get an embed with a list of contributors for the Cursif repository.

    :return: An embed with a list of contributors.
    :rtype: Embed
    """
    embeds: List[Embed] = []

    contributors = repository.get_contributors()
    page_count: int = ceil(contributors.totalCount / 25)

    for i in range(page_count):
        embed: Embed = Embed(
            color=Color.from_str("#171515"),  # github color
            title=f"{repository.name.capitalize()}'s Contributors",
        )

        for contributor in contributors.get_page(i):
            embed.add_field(
                name=contributor.login,
                value=f"{contributor.contributions} Contributions",
                inline=True,
            )

        embeds.append(embed)

    return embeds


def create_repository_button(repository: Repository) -> Button:
    return Button(
        emoji=emojize(":file_folder:"), label="Repository", url=repository.html_url
    )
