from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
from pytz import timezone
from datetime import datetime
from discord.ext.commands import Cog, command
from requests import get
from discord import Embed
from string import capwords
from bot.decorators.config_required import cog_config_required


@cog_config_required("openweather", "api_key")
class WeatherCog(Cog, name="Weather", description="get current weather information from a city"):
    OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5/"

    def __init__(self, bot):
        self.bot = bot
        self.api_key = self.required_config

    def get_timezone(self, city):
        # initialize Nominatim API
        geolocator = Nominatim(user_agent="geoapiExercises")

        # getting Latitude and Longitude
        location = geolocator.geocode(city)

        # pass the Latitude and Longitude
        # into a timezone_at and it return timezone
        timezone_finder = TimezoneFinder()

        result = timezone_finder.timezone_at(
            lng=location.longitude,
            lat=location.latitude)
        return datetime.now(timezone(result))

    def kelvin_to_celsius(self, kelvin):
        return kelvin - 273.15

    def kelvin_to_fahrenheit(self, kelvin):
        return kelvin * 1.8 - 459.67

    async def get_weather(self, city):
        # complete_url to retreive weather info
        response = get(f"{self.OPENWEATHER_BASE_URL}/weather?appid={self.api_key}&q={city}")

        # code 200 means the city is found otherwise, city is not found
        if response.status_code == 200:
            return response.json()
        return None

    @command(name='weather', help='Show weather information in your city', usage="{city}")
    async def weather(self, ctx, *city_input):
        city = capwords(" ".join(city_input))
        # get current date and time from the city
        timezone_city = self.get_timezone(city)
        data_weather = await self.get_weather(city)

        # Now data_weather contains lists of data
        # from the city inputer by the user
        if data_weather:
            icon_id = data_weather["weather"][0]["icon"]
            main = data_weather["main"]
            visibility = data_weather['visibility']
            current_temperature = main["temp"]

            fahrenheit = self.kelvin_to_fahrenheit(int(current_temperature))
            celsius = self.kelvin_to_celsius(int(current_temperature))

            current_pressure = main["pressure"]
            current_humidity = main["humidity"]
            forcast = data_weather["weather"]
            weather_description = forcast[0]["description"]

            embed = Embed(
                color=self.bot.default_color,
                title=city,
                description=timezone_city.strftime('%m/%d/%Y %H:%M'),
            )

            embed.set_image(
                url=f'http://openweathermap.org/img/wn/{icon_id}@2x.png'
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


def setup(bot):
    bot.add_cog(WeatherCog(bot))
