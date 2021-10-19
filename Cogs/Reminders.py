import discord
from discord.ext import commands,tasks
from datetime import datetime,timedelta
import json
import requests
import asyncio

class Reminders(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.WAPI = self.bot.WAPI
        self.reminders = self.bot.reminders
        self.user_reminders = self.bot.user_reminders
        self.timezones = self.bot.timezones
        self.check.start(self.bot.reminders)

    def commit(self):
        reminders=self.reminders
        user_reminders= self.user_reminders
        timezones = self.timezones
        f=open(r"Files/reminders.txt","w")
        Data={"reminders":reminders, "user reminders":user_reminders , "timezones":timezones}
        f.write(str(Data))
        f.close()



    @commands.command(aliases=["settz", "tz"])
    async def timezone(self, ctx, location=None):
        WAPI = self.WAPI
        timezones =  self.timezones

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

        self.commit()
        Embed=discord.Embed(title="TIMEZONE SET ✅",
                            description=f"Timezone set for user {ctx.author.name}",
                            colour=0x2bf707)
        Embed.add_field(name="Location", value=location.capitalize()+"\n _ _", inline=False)
        Embed.add_field(name="Timezone", value=time+"\n _ _", inline = False)
        await msg.edit(content="", embed=Embed)




    @tasks.loop(minutes=1)
    async def check(self, reminders):
        for i in reminders:
            if datetime.utcnow()>=datetime.strptime(i,"%d-%m-%y %I.%M %p"):
                for j in reminders[i]:
                    user=self.bot.get_user(j[0])
                    await user.send(f"You have a reminder for the task : ```\n{j[1]}```")
                    self.user_reminders[user.id].remove(i)
                reminders.pop(i)
                self.commit()
                break



    @commands.command(aliases=["remind_me","R","remind","remindme"])
    async def setreminder(self, ctx, date=None,*,time="12.00 AM"):
        try:
            user_reminders = self.user_reminders
            reminders = self.reminders
            timezones = self.timezones

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
            task = await self.bot.wait_for("message", check=check, timeout=30)


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

            self.commit()

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






    @commands.command(aliases=["Reminder_list","reminder_list","rl"])
    async def reminderlist(self, ctx, user : discord.Member = None):
        user_reminders = self.user_reminders
        reminders = self.reminders

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








    @commands.command()
    async def delete(self, ctx, no: int=0, user=None):
        user_reminders  = self.user_reminders
        reminders = self.reminders

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
        self.commit()

        Embed=discord.Embed(title="REMINDER DELETED",
                            description="Reminder deleted successfully. Please do `!r reminderlist` to view your reminders.",
                            colour=0xdb1414)
        Embed.add_field(name="Date", value=date)
        Embed.add_field(name="Time", value=time)
        Embed.add_field(name="Task", value=f"```\n{taskname}```", inline=False)
        await msg.edit(content="", embed=Embed)



def setup(bot):
    bot.add_cog(Reminders(bot))
