import discord
from discord.ext import commands,tasks
from dotenv import load_dotenv
import os
import asyncio


intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='!r ',intents=intents)


load_dotenv()
TOKEN = os.getenv("TOKEN")
bot.WAPI = os.getenv("WEATHERAPI")




f=open(r"Files/reminders.txt")
Data=eval(f.read())
bot.reminders=Data["reminders"]
#{"date and time":[user.id, task]}
bot.user_reminders=Data["user reminders"]
#{user.id:["date and time"]}
bot.timezones=Data["timezones"]
f.close()
f=open(r"Files/xps.txt")
bot.xps=eval(f.read())
f.close()




for file in os.listdir('./Cogs'):
    if file=="commit.py":
        continue
    if file.endswith('.py'):
        bot.load_extension(f'Cogs.{file[:-3]}')
        print(f"loaded {file}")




bot.run(TOKEN)
