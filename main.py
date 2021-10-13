import discord
from discord.ext import commands,tasks
from datetime import datetime
import os
from dotenv import load_dotenv



load_dotenv()
TOKEN = os.getenv('TOKEN')




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




bot.run(TOKEN)
