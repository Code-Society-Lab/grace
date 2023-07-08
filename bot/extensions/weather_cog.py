from timezonefinder import TimezoneFinder
from pytz import timezone
from datetime import datetime
from discord.ext.commands import Cog, hybrid_command
from requests import get
from discord import Embed
from string import capwords
from lib.config_required import cog_config_required


@cog_config_required("openweather", "api_key", "Generate yours [here](https://openweathermap.org/api)")
class WeatherCog(Cog, name="Weather", description="get current weather information from a city"):
    """A cog that retrieves current weather information for a given city."""
    OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5/"

    def __init__(self, bot):
        self.bot = bot
        self.api_key = self.required_config

    @staticmethod
    def get_timezone(data: any) -> datetime:
        """Get the timezone for the given city.

        :param data: The weather data to get the timezone for.
        :type data: Any | None
        :return: The timezone based on Longitude and Latitude.
        :rtype: datetime.tzinfo
        """
        longitude       = float(data["coord"]['lon'])
        latitude        = float(data["coord"]['lat'])
        timezone_finder = TimezoneFinder()
        
        result = timezone_finder.timezone_at(
            lng=longitude,
            lat=latitude)
        return datetime.now(timezone(str(result)))

    @staticmethod
    def kelvin_to_celsius(kelvin: float) -> float:
        """Convert a temperature in Kelvin to Celsius.

        :param kelvin: The temperature in Kelvin.
        :type kelvin: float
        :return: The temperature in Celsius.
        :rtype: float
        """
        return kelvin - 273.15

    @staticmethod
    def kelvin_to_fahrenheit(kelvin: float) -> float:
        """Convert a temperature in Kelvin to fahrenheit.

        :param kelvin: The temperature in Kelvin.
        :type kelvin: float
        :return: The temperature in fahrenheit.
        :rtype: float
        """
        return kelvin * 1.8 - 459.67

    async def get_weather(self, city: str):
        """Retrieve weather information for the specified city.

        :param city: The name of the city to retrieve weather information for
        :type city: str
        :return: A dictionary containing the weather information, or None if the city was not found
        :rtype: dict
        """
        # complete_url to retreive weather info
        response = get(f"{self.OPENWEATHER_BASE_URL}/weather?appid={self.api_key}&q={city}")

        # code 200 means the city is found otherwise, city is not found
        if response.status_code == 200:
            return response.json()
        return None

    @hybrid_command(name='weather', help='Show weather information in your city', usage="{city}")
    async def weather(self, ctx, *, city_input: str):
        """Display weather information for the specified city.

        :param ctx: the Discord context for the command
        :type ctx: Context
        :param city_input: The name of the city to display weather information for
        :type city_input: str
        :return: This function sends an embed message to the Discord channel
        """
        if ctx.interaction:
            await ctx.interaction.response.defer()

        city          = capwords(city_input)
        data_weather  = await self.get_weather(city)
        timezone_city = self.get_timezone(data_weather)

        # Now data_weather contains lists of data
        # from the city inputer by the user
        if data_weather:
            icon_id    = data_weather["weather"][0]["icon"]
            main       = data_weather["main"]
            visibility = data_weather['visibility']
            current_temperature = main["temp"]

            fahrenheit = self.kelvin_to_fahrenheit(int(current_temperature))
            celsius    = self.kelvin_to_celsius(int(current_temperature))

            feels_like            = main["feels_like"]
            feels_like_fahrenheit = self.kelvin_to_fahrenheit(int(feels_like))
            feels_like_celsius    = self.kelvin_to_celsius(int(feels_like))

            current_pressure    = main["pressure"]
            current_humidity    = main["humidity"]
            forcast             = data_weather["weather"]
            weather_description = forcast[0]["description"]

            embed = Embed(
                color=self.bot.default_color,
                title=city,
                description=timezone_city.strftime('%m/%d/%Y %H:%M'),
            )

            embed.set_image(
                url=f'https://openweathermap.org/img/wn/{icon_id}@2x.png'
            )
            embed.add_field(
                name="Description",
                value=capwords(weather_description),
                inline=False
            )
            embed.add_field(
                name="Visibility",
                value=f"{visibility}m | {round(visibility * 3.280839895)}ft",
                inline=False
            )
            embed.add_field(
                name="Temperature",
                value=f"{round(fahrenheit, 2)}°F | {round(celsius, 2)}°C",
                inline=False
            )
            embed.add_field(
                name="Feels Like",
                value=f"{round(feels_like_fahrenheit, 2)}°F | {round(feels_like_celsius, 2)}°C",
                inline=False
            )
            embed.add_field(
                name="Atmospheric Pressure",
                value=f"{current_pressure} hPa",
                inline=False
            )
            embed.add_field(
                name="Humidity",
                value=f"{current_humidity}%",
                inline=False
            )
        else:
            embed = Embed(
                color=self.bot.default_color,
                description=f"{city} No Found!",
            )
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(WeatherCog(bot))
