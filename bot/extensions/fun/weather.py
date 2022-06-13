from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
import pytz
from pytz import country_timezones, timezone
from datetime import datetime
from discord.ext.commands import Cog, command
import requests
from discord import Embed
import time
import string

from discord.utils import parse_time

class WeatherCog(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name='weather', help='Show weather information in your city', usage="{city}")
    async def my_command(self, ctx, *city_input):
        # get all argument inputed by the user 
        # on discord and join them together 
        # (handle double-words/argument cities)
        city = " "
        city = string.capwords(city.join(city_input))
    
        # initialize Nominatim API
        geolocator = Nominatim(user_agent="geoapiExercises")
        # city_name = city.capitalize()
        # getting Latitude and Longitude
        location = geolocator.geocode(city)
    
        # pass the Latitude and Longitude
        # into a timezone_at
        # and it return timezone
        obj = TimezoneFinder()

        # returns timezone
        result = obj.timezone_at(lng=location.longitude, lat=location.latitude)
        timezone_city = datetime.now(pytz.timezone(result))
        timezone_city = timezone_city.strftime('%m/%d/%Y %H:%M')

        # Enter your API key here
        api_key="441df3a5cadc2498e093c0367cae6817"
        # base_url variable to store url
        base_url = "http://api.openweathermap.org/data/2.5/weather?"
        # Give city name

        city_name = str(city)
        # complete_url variable to store complete url address
        complete_url = base_url + "appid=" + api_key + "&q=" + city_name
        # get method of requests module return response object
        response = requests.get(complete_url)
        # json method of response object convert json format data into python format data
        data_weather = response.json()

        # Now data_weather contains list of nested dictionaries, check the value of "cod" key is not equal to
        # "404", means city is found otherwise, city is not found
        if data_weather["cod"] != "404":
            # get icon id
            icon_id = data_weather["weather"][0]["icon"]
            # store the value of "main" key in variable main
            main = data_weather["main"]
            # store the value of visibility into the variable visibility
            visibility = data_weather['visibility']
            # store the value corresponding to the "temp" key of main
            current_temperature = main["temp"]
            # Convert in Fahrenheit
            fahrenheit = round((int(current_temperature)) * 1.8 - 459.67,2)
            celsius = round((int(current_temperature) - 273.15), 2)
            # store the value corresponding to the "pressure" key of main
            current_pressure = main["pressure"]
            # store the value corresponding to the "humidity" key of main
            current_humidiy = main["humidity"]
            # store the value of "weather" key in variable forcast
            forcast = data_weather["weather"]
            # store the value corresponding to the "description" key at the 0th index of forcast
            weather_description = forcast[0]["description"]
            # print following values
            embed = Embed(
            color = self.bot.default_color,
            title = f"{city}",
                description=f"{timezone_city}",
            )
        
            embed.set_image(
            url='http://openweathermap.org/img/wn/' + icon_id + '@2x.png'
            )
            embed.add_field(
                name="Description",
                value=f"{str(string.capwords(weather_description))}"
                "\u200b",
                inline=False
            )
            embed.add_field(
                name="Visibility",
                value=f"{visibility}m | {round(visibility*3.280839895)}ft"
                "\u200b",
                inline=False
            )
            embed.add_field(
            name = "Temperature",
                value=f"{fahrenheit}°F | {celsius}°C"
                    "\u200b",
            inline = False
            )
            embed.add_field(
            name = "Atmospheric Pressure",
            value = f"{current_pressure} hPa"
                    "\u200b",
            inline = False
            )
            embed.add_field(
            name = "Humidity",
            value = f"{current_humidiy}%"
                    "\u200b",
            inline = False
            )

            await ctx.send(embed=embed)
        else:
            embeded = Embed(
                color=self.bot.default_color,
                # title=f"{city}",
                description=f"{city.capitalize()} No Found!",
            )
            await ctx.send(embed=embeded)

def setup(bot):
    bot.add_cog(WeatherCog(bot))
