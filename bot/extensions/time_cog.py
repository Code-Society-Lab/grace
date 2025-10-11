import pytz
import re

from discord.ext.commands import Cog
from datetime import datetime, timedelta
from dateutil import parser
from discord import Message

# Mapping for common timezone abbreviations to their UTC offsets
timezone_abbreviations = {
    # North American
    "pst": "America/Los_Angeles",      # Pacific Standard Time
    "pdt": "America/Los_Angeles",      # Pacific Daylight Time
    "mst": "America/Denver",           # Mountain Standard Time
    "mdt": "America/Denver",           # Mountain Daylight Time
    "cst": "America/Chicago",          # Central Standard Time
    "cdt": "America/Chicago",          # Central Daylight Time
    "est": "America/New_York",         # Eastern Standard Time
    "edt": "America/New_York",         # Eastern Daylight Time

    # International standards
    "gmt": "Etc/GMT",                  # Greenwich Mean Time
    "utc": "UTC",                      # Coordinated Universal Time

    # European
    "bst": "Europe/London",            # British Summer Time
    "cet": "Europe/Paris",             # Central European Time
    "cest": "Europe/Paris",            # Central European Summer Time

    # Asia-Pacific
    "hkt": "Asia/Hong_Kong",           # Hong Kong Time
    "ist": "Asia/Kolkata",             # India Standard Time
    "jst": "Asia/Tokyo",               # Japan Standard Time
    "aest": "Australia/Sydney",        # Australian Eastern Standard Time
    "aedt": "Australia/Sydney",        # Australian Eastern Daylight Time

    # TODO: find a way to fetch all timezones dynamically
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

    def _build_regex(self) -> str:
        keys = timezone_abbreviations.keys()
        escaped_keys = [re.escape(key) for key in keys]
        joined = "|".join(escaped_keys)

        return rf"\b({joined})\b"

    @Cog.listener()
    async def on_message(self, message: Message) -> None:
        if message.author.bot:
            return

        time_str = message.content.lower()
        tz_pattern = self._build_regex()
        if not re.search(tz_pattern, time_str):
            return  # process only when timezone in message

        utc = pytz.UTC
        now_utc = datetime.now(utc)

        time_str = " ".join(time_str.split())
        time_str = self._build_relative_date(time_str, now_utc)

        try:
            timestamp = self._build_timestamp(utc, time_str)
            await message.reply(f"<t:{timestamp}:F>")
        except Exception:
            pass


async def setup(bot):
    await bot.add_cog(TimeCog(bot))
