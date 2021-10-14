import discord
from discord.ext import commands,tasks
from datetime import datetime
from dotenv import load_dotenv
import os
import json
import requests

load_dotenv()
TOKEN = os.getenv("TOKEN")
WAPI = os.getenv("WEATHERAPI")





f=open("reminders.txt")
reminders=(eval(f.read()))
f.close()

def commit():
    f=open("reminders.txt","w")
    f.write(str(reminders))
    f.close()




intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='!r ',intents=intents)




@bot.event
async def on_ready():
    print("Bot online!")
    check.start(reminders)




@tasks.loop(minutes=1)
async def check(reminders):
    for i in reminders:
        if datetime.now().strftime("%d-%m-%Y %I:%M %p")==i:
            for j in reminders[i]:
                user=bot.get_user(j[0])
                await user.send("You have a reminder for the task : "+j[1])
            reminders.pop(i)
            commit()
            break


@bot.command(aliases=["remind_me","R"])
async def remind(ctx):

    def check(m):
        return m.channel==ctx.channel and m.author==ctx.author
    format="%d-%m-%Y"

    try:
        await ctx.send("Enter task date(dd-mm-yyyy) : ")
        date = await bot.wait_for("message", check=check, timeout=120)
        try:
            datetime.strptime(date.content,format)
        except ValueError:
            await ctx.send("Incorrect format of date, please try again!")
    except Exception:
        await ctx.send("No reply, session timed out!")

    try:
        await ctx.send("Enter time(hh:mm AM/PM): ")
        time = await bot.wait_for("message", check=check, timeout=120)
        try:
            datetime.strptime(time.content.upper(),"%I:%M %p")
        except ValueError:
            await ctx.send("Incorrect format of time, please try again!")
        print(date.content+time.content)
    except Exception:
        await ctx.send("No reply, session timed out!")

    try:
        await ctx.send("Enter task : ")
        task = await bot.wait_for("message", check=check, timeout=180)
    except Exception:
        await ctx.send("No reply, session timed out!")

    dt=date.content+" "+time.content
    print(dt)
    if dt not in reminders:
        reminders[dt]=[[ctx.author.id,task.content]]
    else:
        reminders[dt].append([ctx.author.id,task.content])
    print(reminders)

    await ctx.send("Reminder added!")
    commit()




@bot.command(aliases=["Reminder_list","reminder_list"])
async def rl(ctx):
    Embed=discord.Embed(title="REMINDERS",description="All the reminders based on date-")
    dt=list(reminders)
    dt.sort()

    for i in dt:
        val=""
        for j in reminders[i]:
            user=bot.get_user(j[0])
            val+=f"{j[1]} - added by `{user.name}`\n"
        Embed.add_field(name=i, value=val, inline=False)

    await ctx.send(embed=Embed)




@bot.command()
async def delete(ctx):
    def check(m):
        return m.channel==ctx.channel and m.author==ctx.author
    format="%d-%m-%Y"

    try:
        await ctx.send("Enter delete task date(dd-mm-yyyy) : ")
        date = await bot.wait_for("message", check=check, timeout=120)
        try:
            datetime.strptime(date.content,format)
        except ValueError:
            await ctx.send("Incorrect format of date, please try again!")
    except Exception:
        await ctx.send("No reply, session timed out!")

    try:
        await ctx.send("Enter delete task time(hh:mm AM/PM): ")
        time = await bot.wait_for("message", check=check, timeout=120)
        try:
            datetime.strptime(time.content.upper(),"%I:%M %p")
        except ValueError:
            await ctx.send("Incorrect format of time, please try again!")

    except Exception:
        await ctx.send("No reply, session timed out!")

    try:
        await ctx.send("Enter task : ")
        task = await bot.wait_for("message", check=check, timeout=180)
        task = task.content
    except Exception:
        await ctx.send("No reply, session timed out!")

    dt=date.content+" "+time.content
    print(dt)
    if dt not in reminders:
        await ctx.send("There is no task on the given date!")
    else:
        print("task available")

        tasks=[x[1] for x in reminders[dt]]
        print(tasks)

        if task not in tasks:
            await ctx.send("Task not found!")
        else:
            pos=tasks.index(task)
            if ctx.author.id!=reminders[dt][pos][0]:
                await ctx.send("You cannot delete others reminders!")
            else:
                if len(tasks)!=1:
                    print(reminders[dt].pop(pos))
                else:
                    print(reminders.pop(dt))
                await ctx.send("Task deleted!")
    commit()



#Weather_command
@bot.command(aliases=["temp","climate","temperature"])
async def weather(ctx,location):
    url=f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={WAPI}&units=metric"
    data=json.loads(requests.get(url).content)
    temp=data["main"]
    weather=data["weather"][0]["main"]+"("+data["weather"][0]["description"]+")"
    image=data["weather"][0]["icon"]+".png"
    place=data["name"]
    file = discord.File(f"icons\{image}", filename="image_url.png")
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


    Embed=discord.Embed(title=f"Weather:white_sun_rain_cloud: in {location} is currently : ", description=weather, timestamp=datetime.now(), colour=colour)
    Embed.add_field(name="Temperature(°C):", value=str(temp["temp"]), inline=False)
    Embed.add_field(name="Feels like(°C):",value=str(temp["feels_like"]), inline=False)
    Embed.add_field(name="Humidity:", value=str(temp["humidity"])+"%", inline=False)
    Embed.add_field(name="Cloudiness:", value=str(data["clouds"]["all"])+"%", inline=False)
    Embed.add_field(name="Atmospheric Pressure:", value=str(temp["pressure"])+"hPa",inline=False)
    Embed.set_thumbnail(url="attachment://image_url.png")


    await ctx.send(embed=Embed, file=file)





bot.run(TOKEN)
