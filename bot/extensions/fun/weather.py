from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
from pytz import country_timezones, timezone
from datetime import datetime
from discord.ext.commands import Cog, command
from requests import get
from discord import Embed
from string import capwords


class WeatherCog(Cog, name="Weather", description="get current weather information from a city"):
    def __init__(self, bot):
        self.bot = bot
    
    @command(name='weather', help='Show weather information in your city', usage="{city}")
    async def weather(self, ctx, *city_input):
        city = capwords(" ".join(city_input))

        # initialize Nominatim API
        geolocator = Nominatim(user_agent="geoapiExercises")
        
        # getting Latitude and Longitude
        location = geolocator.geocode(city)

        # pass the Latitude and Longitude
        # into a timezone_at
        # and it return timezone
        timezone_finder = TimezoneFinder()

        result = timezone_finder.timezone_at(
            lng=location.longitude, 
            lat=location.latitude)
        timezone_city = datetime.now(timezone(result))
        timezone_city = timezone_city.strftime('%m/%d/%Y %H:%M')

        api_key = "441df3a5cadc2498e093c0367cae6817"
        base_url = "http://api.openweathermap.org/data/2.5/weather?"

        # complete_url to retreive weather info
        complete_url = base_url + "appid=" + api_key + "&q=" + city
        response = get(complete_url)
        data_weather = response.json()

        # Now data_weather contains list of nested dictionaries, 
        # check the value of "cod" if key is equal to 200
        # it means the city is found otherwise, city is not found
        if data_weather["cod"] == 200:
            icon_id = data_weather["weather"][0]["icon"]    # get image icon id
            main = data_weather["main"]                     # get the main datas
            visibility = data_weather['visibility']         # get current visibility
            current_temperature = main["temp"]              # get current temperature  
            fahrenheit = round((int(current_temperature)) * 1.8 - 459.67, 2)    # convert kelvin to fahrenheit
            celsius = round((int(current_temperature) - 273.15), 2)             # convert kelvin to celsius
            current_pressure = main["pressure"]             # get current pressure athmospheric
            current_humidity = main["humidity"]             # get current humidity
            forcast = data_weather["weather"]               # get current weather description
            weather_description = forcast[0]["description"]
            
            embed = Embed(
                color=self.bot.default_color,
                title=f"{city}",
                description=f"{timezone_city}",
            )

            embed.set_image(
                url='http://openweathermap.org/img/wn/' 
                + icon_id 
                +'@2x.png'
            )
            embed.add_field(
                name="Description",
                value=f"{capwords(weather_description)}",
                inline=False
            )
            embed.add_field(
                name="Visibility",
                value=f"{visibility}m | {round(visibility*3.280839895)}ft",
                inline=False
            )
            embed.add_field(
                name="Temperature",
                value=f"{fahrenheit}°F | {celsius}°C",
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
