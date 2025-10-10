import pytz

from discord.ext.commands import Cog
from datetime import datetime, timedelta
from dateutil import parser
from discord import Message

# Mapping for common timezone abbreviations to their UTC offsets
timezone_abbreviations = {
    "pst": "America/Los_Angeles",
    "pdt": "America/Los_Angeles",
    "est": "America/New_York",
    "edt": "America/New_York",
    "utc": "UTC",
    # TODO: Maybe add more timezone or find a way to fetch them dynamically
    # maybe from pytz or another library?
}


class TimeCog(
    Cog,
    name="Time",
    description="Convert time to UTC-based timestamp."
):
    def __init__(self, bot):
        self.bot = bot

    def _build_timestamp(self, utc, time_str: str) -> int:
        parsed_time = parser.parse(time_str, fuzzy=True)

        # Detect abbreviation in the message
        tz_found = False
        for abbr, tz_name in timezone_abbreviations.items():
            if abbr in time_str:
                tz = pytz.timezone(tz_name)
                if parsed_time.tzinfo is None:
                    parsed_time = tz.localize(parsed_time)
                else:
                    parsed_time = parsed_time.astimezone(tz)
                tz_found = True
                break

        if not tz_found:
            parsed_time = utc.localize(parsed_time.replace(tzinfo=None))

        return int(parsed_time.timestamp())

    def _build_relative_date(self, time_str: str, now_utc: datetime) -> str:
        # Handle relative dates
        if "today" in time_str:
            date_str = now_utc.strftime('%Y-%m-%d')
            time_str = time_str.replace("today", date_str)
        elif "tomorrow" in time_str:
            date_str = (now_utc + timedelta(days=1)).strftime('%Y-%m-%d')
            time_str = time_str.replace("tomorrow", date_str)

        return time_str

    @Cog.listener()
    async def on_message(self, message: Message) -> None:
        if message.author.bot:
            return

        utc = pytz.UTC
        now_utc = datetime.now(utc)

        time_str = message.content.lower()
        time_str = " ".join(time_str.split())
        time_str = self._build_relative_date(time_str, now_utc)

        try:
            timestamp = self._build_timestamp(utc, time_str)
            await message.channel.send(f"<t:{timestamp}:F>")
        except Exception as e:
            await message.channel.send(f"Could not parse time. Error: {str(e)}")


async def setup(bot):
    await bot.add_cog(TimeCog(bot))
