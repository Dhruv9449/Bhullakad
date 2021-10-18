import discord
from discord.ext import commands,tasks
from datetime import datetime,timedelta
from dotenv import load_dotenv
import os
import json
import requests
from random import randint
import asyncio
from pprint import pprint

load_dotenv()
TOKEN = os.getenv("TOKEN")
WAPI = os.getenv("WEATHERAPI")





f=open("reminders.txt")
Data=eval(f.read())
reminders=Data["reminders"]
#{"date and time":[user.id, task]}
user_reminders=Data["user reminders"]
#{user.id:["date and time"]}
timezones=Data["timezones"]
f.close()
f=open("xps.txt")
xps=eval(f.read())
f.close()


def commit(t):
    if t=="r":
        f=open("reminders.txt","w")
        Data={"reminders":reminders, "user reminders":user_reminders , "timezones":timezones}
        f.write(str(Data))
        f.close()
    else:
        f=open("xps.txt","w")
        f.write(str(xps))
        f.close()





intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='!r ',intents=intents)




async def xps_inc(msg):
    user=msg.author.id
    if user not in xps:
        xps[user]=[randint(1,5),0]
    else:
        xps[user][0]+=randint(1,5)
    xp=xps[user][0]
    levelup=lvlup(user,xp)
    curlvl=xps[user][1]
    if levelup==1:
        user=bot.get_user(user)
        await msg.channel.send(f"Congrats {user.mention}! you just leveled up to {curlvl}")
    commit("l")


def lvlup(user,xp):
    curlvl=xps[user][1]
    nextlvl=int(xp**(1/4))
    if curlvl!=nextlvl:
        xps[user][1]+=1
        return 1
    else:
        return 0



@bot.event
async def on_message(msg):
    if msg.author.bot:
        return
    await xps_inc(msg)
    await bot.process_commands(msg)



@bot.event
async def on_ready():
    print("Bot online!")
    check.start(reminders)


@bot.command()
async def init(ctx):
    await ctx.trigger_typing()
    msg= await ctx.send("```Initializing.```")
    for i in range(10):

        await msg.edit(content="```Initializing..```")

        await msg.edit(content="```Initializing...```")

        await msg.edit(content="```Initializing.```")

    await msg.edit(content="```Initializing..```")

    await msg.edit(content="```Initializing...```")

    await msg.edit(content="```Initialized successfully!```")



@bot.command(aliases=["settz", "tz"])
async def timezone(ctx,location=None):
    if location == None:
        Embed=discord.Embed(title=" Set Timezone!",
                            description="Set a timezone by adding your location! `!r timezone <location>`",
                            colour=0xdb1414)
        await ctx.send(embed=Embed)
        return

    url=f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={WAPI}"
    data=json.loads(requests.get(url).content)
    timezone=data["timezone"]
    timezones[ctx.author.id]=timezone
    time=timezone/60/60
    hour=int(time)
    minutes=str(int((time-hour)*60)).zfill(2)
    hour=str(hour).zfill(2)
    if time>0:
        time=f"GMT +{hour}:{minutes}"
    else:
        time=f"GMT {hour}:{minutes}"



    msg = await ctx.send("```\nInitializing...```")
    await ctx.trigger_typing()
    await asyncio.sleep(2)
    await msg.edit(content=f"```\nFetching location {location.capitalize()}...```")
    await asyncio.sleep(2)
    await msg.edit(content=f"```\nSetting timezone {time}...```")
    await asyncio.sleep(2)

    commit("r")
    Embed=discord.Embed(title="TIMEZONE SET ✅",
                        description=f"Timezone set for user {ctx.author.name}",
                        colour=0x2bf707)
    Embed.add_field(name="Location", value=location.capitalize()+"\n _ _", inline=False)
    Embed.add_field(name="Timezone", value=time+"\n _ _", inline = False)
    await msg.edit(content="", embed=Embed)




@bot.command()
async def top(ctx):
    text="```py\n📋 Rank | Name \n\n"
    values=[tuple(x) for x in xps.values()]
    rev=dict(zip(values,xps.keys()))
    values=list(rev)
    values.sort(reverse=True)
    sno=0
    for i in values:
        sno+=1
        user=bot.get_user(rev[i])
        text+=f"[{sno}]     > #{user.name}:\n             Total Score: {i[0]}\n"
        if ctx.author==user:
            user_sn=sno

    text+=f"\n------------------------------------------\n#Your Placing Stats \n😀 Rank: {user_sn}     Total Score: {xps[ctx.author.id][0]}```"

    await ctx.send(content=text)



@tasks.loop(minutes=1)
async def check(reminders):
    for i in reminders:
        if datetime.utcnow().strftime("%d-%m-%y %I.%M %p")>=i:
            for j in reminders[i]:
                user=bot.get_user(j[0])
                await user.send(f"You have a reminder for the task : ```\n{j[1]}```")
                user_reminders[user.id].remove(i)
            reminders.pop(i)
            commit("r")
            break



@bot.command(aliases=["remind_me","R","remind","remindme"])
async def setreminder(ctx, date=None,*,time="12.00 AM"):
    try:
        userid=ctx.author.id
        if userid not in timezones:
            Embed=discord.Embed(title="ERROR !",
                                description="You have not added your timezone yet! `!r timezone <location>`",
                                colour=0xdb1414)
            await ctx.send(embed=Embed)
            return

        timezone=timedelta(seconds=timezones[userid])

        if date==None:
            Embed=discord.Embed(title="ERROR !",
                                description="Enter a date please! Please try again using `!r setreminder`",
                                colour=0xdb1414)
            await ctx.send(embed=Embed)
            return
        elif date.lower()=="today":
            date=(datetime.utcnow() + timezone).strftime("%d-%m-%y")


        time.upper()
        time=time.replace(":",".")
        date=date.replace("/","-")
        date=date.replace(".","-")
        format="%d-%m-%y %I.%M %p"
        ogdt=date+" "+time
        ogtime = datetime.strptime(ogdt,format)
        utctime =  ogtime - timezone

        if datetime.utcnow()>=utctime:
            Embed=discord.Embed(title="ERROR !",
                                description="Date and time has already passed! Please try again using `!r setreminder`",
                                colour=0xdb1414)
            await ctx.send(embed=Embed)
            return

        ogdt = ogtime.strftime(format)
        utcdt = utctime.strftime(format)

        def check(m):
            return m.channel==ctx.channel and m.author==ctx.author

        await ctx.send("```\nPlease enter Task : ```")
        task = await bot.wait_for("message", check=check, timeout=30)


        msg = await ctx.send("```\nInitializing...```")
        await ctx.trigger_typing()
        await asyncio.sleep(2)
        task=task.content
        if utcdt not in reminders:
            reminders[utcdt]=[[userid, task, ogdt]]

        else:
            reminders[utcdt].append([userid, task, ogdt])


        if userid not in user_reminders:
            user_reminders[ctx.author.id]=[utcdt]
        else:
            user_reminders[ctx.author.id].append(utcdt)


        await ctx.trigger_typing()
        await msg.edit(content="```\nFetching reminder details..```")
        await asyncio.sleep(2)
        await msg.edit(content=f"```\nAdding reminder for date {date}...```")
        await asyncio.sleep(2)

        commit("r")

        Embed=discord.Embed(title="REMINDER ADDED ✅",
                            description="Reminder added successfully. Please do `!r reminderlist` to view your reminders.",
                            colour=0x2bf707)
        Embed.add_field(name="Date", value=date)
        Embed.add_field(name="Time", value=time)
        Embed.add_field(name="Task", value=f"```\n{task}```", inline=False)
        await msg.edit(content="", embed=Embed)

    except ValueError:
        Embed=discord.Embed(title="ERROR!",
                            description="Invalid format of date or time. Correct format-\n ```Date - dd-mm-yy \nTime - hh.mm AM/PM \n\nExample - !r setreminder 19-06-21 12:00 AM```",
                            colour=0xdb1414)
        await ctx.send(embed=Embed)
        return
    except asyncio.TimeoutError:
        Embed=discord.Embed(title="Error!",
                            description="Session timed out! Please try again using `!r setreminder`",
                            colour=0xdb1414)
        await ctx.send(embed=Embed)






@bot.command(aliases=["Reminder_list","reminder_list","rl"])
async def reminderlist(ctx, user : discord.Member = None):
    if user==None:
        user = ctx.author
    if user.id not in user_reminders or user_reminders[user.id]==[]:
        Embed=discord.Embed(title="ERROR !",
                            description="You don't have any reminders! To add reminder use - `!r setreminder`",
                            colour=0xdb1414)
        await ctx.send(embed=Embed)
        return

    reminderdates=list(set(user_reminders[user.id]))
    reminderdates.sort()

    sno=0
    Embed=discord.Embed(title="REMINDERS 📅", description=f"Reminders of {user.name}",timestamp=datetime.utcnow())
    for i in reminderdates:
        data = reminders[i]
        data.sort()
        text=""
        reminderdate=data[0][2][:8]
        remindertime=data[0][2][9:]
        for j in data:
            if j[0]==user.id:
                sno+=1
                task=j[1]
                Embed.add_field(name=f"{sno}. {task}",
                                value=f"**Date : **{reminderdate}\n**Time : **{remindertime}\n _ _\n _ _",
                                inline=False)

    await ctx.send(embed=Embed)








@bot.command()
async def delete(ctx, no: int=0, user=None):
    if user==None:
        user = ctx.author
    if user.id not in user_reminders or user_reminders[user.id]==[]:
        Embed=discord.Embed(title="ERROR !",
                            description="You don't have any reminders! To add reminder use - `!r setreminder`",
                            colour=0xdb1414)
        await ctx.send(embed=Embed)
        return

    tasks={}
    reminderdates=list(set(user_reminders[user.id]))
    reminderdates.sort()

    sno=0
    for i in reminderdates:
        data = reminders[i]
        data.sort()
        pos=0
        for j in data:
            if j[0]==user.id:
                sno+=1
                tasks[sno]=[i,j,pos]
                pos+=1


    if no not in tasks:
        Embed=discord.Embed(title="ERROR !",
                            description="You haven't entered a valid value of task number, please do - `!r reminderlist` to view your reminders",
                            colour=0xdb1414)
        await ctx.send(embed=Embed)
        return

    utcdate=tasks[no][0]
    taskname=tasks[no][1][1]
    pos=tasks[no][2]
    date=tasks[no][1][2][:8]
    time=tasks[no][1][2][9:]

    msg = await ctx.send(f"```\nFetching reminder number {no}...```")
    await ctx.trigger_typing()
    await asyncio.sleep(2)
    await msg.edit(content=f"```\nFetching date {date}...```")
    await asyncio.sleep(1)
    await msg.edit(content=f"```\nDeleting task :\"{taskname}\"...```")
    await asyncio.sleep(1)

    if len(reminders[utcdate])==1:
        reminders.pop(utcdate)
    else:
        reminders[utcdate].pop(pos)
    user_reminders[user.id].remove(utcdate)
    commit("r")

    Embed=discord.Embed(title="REMINDER DELETED",
                        description="Reminder deleted successfully. Please do `!r reminderlist` to view your reminders.",
                        colour=0xdb1414)
    Embed.add_field(name="Date", value=date)
    Embed.add_field(name="Time", value=time)
    Embed.add_field(name="Task", value=f"```\n{taskname}```", inline=False)
    await msg.edit(content="", embed=Embed)
















#Weather_command
@bot.command(aliases=["temp","climate","temperature"])
async def weather(ctx,location):
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





bot.run(TOKEN)
