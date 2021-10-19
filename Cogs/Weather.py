import discord
from discord.ext import commands
from datetime import datetime
import json
import requests
import asyncio



class Weather(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.WAPI = self.bot.WAPI


    #Weather_command
    @commands.command(aliases=["temp","climate","temperature"])
    async def weather(self, ctx, location):
        WAPI = self.WAPI


        url=f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={WAPI}&units=metric"
        data=json.loads(requests.get(url).content)
        temp=data["main"]
        weather=data["weather"][0]["main"]+"("+data["weather"][0]["description"]+")"
        image=data["weather"][0]["icon"]+".png"
        place=data["name"]
        file = discord.File(fr"icons/{image}", filename="image_url.png")
        image_url=f"https://github.com/yuvraaaj/openweathermap-api-icons/blob/master/icons/{image}"
        sunny=0xe00707
        rainy=0x770e0
        snowy=0x07d9e0
        cloudy=0xbadfe6
        night=0x080729
        if image[:3] in ["01d","02d","03d"]:
            colour=sunny
        elif image[:3] in ["09d","09n","10n","10d","11n","11d"]:
            colour=rainy
        elif image[:3] in ["01n","02n","03n"]:
            colour=night
        elif image[:3] in ["13n","13d"]:
            colour=snowy
        else:
            colour=cloudy


        Embed=discord.Embed(title=f"Weather:white_sun_rain_cloud: in {place} is currently : ", description=weather, timestamp=datetime.utcnow(), colour=colour)
        Embed.add_field(name="Temperature(°C):", value=str(temp["temp"]), inline=False)
        Embed.add_field(name="Feels like(°C):",value=str(temp["feels_like"]), inline=False)
        Embed.add_field(name="Humidity:", value=str(temp["humidity"])+"%", inline=False)
        Embed.add_field(name="Cloudiness:", value=str(data["clouds"]["all"])+"%", inline=False)
        Embed.add_field(name="Atmospheric Pressure:", value=str(temp["pressure"])+"hPa",inline=False)
        Embed.set_thumbnail(url="attachment://image_url.png")


        await ctx.send(embed=Embed, file=file)



def setup(bot):
  bot.add_cog(Weather(bot))
