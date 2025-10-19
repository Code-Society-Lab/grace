import re
from datetime import datetime, timedelta
from discord import Embed
from discord.ext.commands import Cog, hybrid_command
from pytz import timezone
from typing import Match


class ReminderCog(
    Cog,
    name="Reminder",
    description="Handles reminder functionalities within the Discord bot.",
):
    """A Discord Cog that manages user reminders."""

    def __init__(self, bot):
        self.bot = bot
        self.jobs = []
        self.timezone = timezone("US/Eastern")

    def cog_unload(self):
        """Clean up any jobs this cog created."""
        for job in self.jobs:
            self.bot.scheduler.remove_job(job.id)

    def _build_embed(self, title: str, message: str, author: str) -> Embed:
        """Builds a Discord embed with the given description.

        :param title: The title of the embed.
        :param message: The description/message of the embed.
        :param author: The author of the embed.

        :return: The constructed Embed object.
        """
        embed = Embed(
            color=self.bot.default_color,
            title=f"**{title}**",
            description=message,
            timestamp=datetime.now(),
        )
        embed.set_author(name=author)
        embed.set_thumbnail(
            url=(
                "https://external-content.duckduckgo.com/iu/?u="
                "https%3A%2F%2Fstatic.vecteezy.com%2Fsystem%2Fresources%2Fpreviews"
                "%2F012%2F067%2F332%2Foriginal%2Fhand-holding-a-stopwatch-timer-png.png"
                "&f=1&nofb=1"
            )
        )
        return embed

    def _convert_to_timedelta(self, match: Match[str]) -> timedelta:
        """Converts the parsed time format into a timedelta.

        :param match: The timer from the user containing amount and unit.
                    amount: The amount of time before the reminder.
                    unit: The unit of time (s=second, m=minute, h=hour, d=day).

        :return: The constructed timedelta for the reminder.
        """
        amount, unit = match.groups()
        amount = int(amount)
        match unit:
            case "s":
                return timedelta(seconds=amount)
            case "m":
                return timedelta(minutes=amount)
            case "h":
                return timedelta(hours=amount)
            case "d":
                return timedelta(days=amount)

    @hybrid_command(
        name="reminder", help="Set a reminder with a message", usage="{timer} {message}"
    )
    async def reminder(self, ctx, timer: str, *, message: str) -> None:
        """
        Set a reminder for the user.

        :param ctx: Command context.
        :param timer: Time after which to remind the user such as '10m', '2h', '1d'.
        :param message: The reminder message.
        """
        time_pattern = re.compile(r"(\d+)([smhd])")
        match = time_pattern.fullmatch(timer)
        if not match:
            await ctx.send(
                "Invalid time format! Use '10m' for 10 minutes,'2h' for 2 hours, etc."
            )
            return

        reminder_delta = self._convert_to_timedelta(match)
        reminder_time = datetime.now(self.timezone) + reminder_delta

        self.jobs.append(
            self.bot.scheduler.add_job(
                self.send_reminder,
                "date",
                run_date=reminder_time,
                args=[ctx, message],
                id=f"reminder_{ctx.author.id}_{datetime.now().timestamp()}",
            )
        )

        reminder_time = (
            ctx.message.created_at + reminder_delta  # convert to the user timezone
        )
        timestamp = int(reminder_time.timestamp())
        embed = self._build_embed(
            "Reminder Set",
            f"Reminder set for {timer} from now!\n"
            f"You will be reminded on **<t:{timestamp}:F>**.",
            ctx.author.display_name,
        )
        await ctx.send(embed=embed, ephemeral=True)

    async def send_reminder(self, ctx, message: str) -> None:
        """Sends the reminder to the user when the scheduler triggers it.

        :param ctx: Command context.
        :param message: The reminder message.
        """
        embed = self._build_embed("Your Reminder", message, ctx.author.display_name)
        await ctx.send(f"<@{ctx.author.id}>", embed=embed)


async def setup(bot):
    await bot.add_cog(ReminderCog(bot))
