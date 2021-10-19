import discord
from discord.ext import commands,tasks
from random import randint

class Levelling(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.xps = bot.xps


    def commit(self):
        xps = self.xps
        f=open(r"Files/xps.txt","w")
        f.write(str(xps))
        f.close()


    @commands.command()
    async def top(self,ctx):
        xps = self.xps
        bot = self.bot
        text="```py\n📋 Rank | Name \n\n"
        values=[tuple(x) for x in xps.values()]
        rev=dict(zip(values,xps.keys()))
        for i in rev:
            print(i,rev[i])
        values=list(rev)
        values.sort(reverse=True)
        print(values)
        sno=0
        for i in values:
            sno+=1
            print(rev[i])
            user=bot.get_user(rev[i])
            rev.pop(i)
            print(rev)
            text+=f"[{sno}]     > #{user.name}:\n             Total Score: {i[0]}\n"
            if ctx.author==user:
                user_sn=sno

        text+=f"\n------------------------------------------\n#Your Placing Stats \n😀 Rank: {user_sn}     Total Score: {xps[ctx.author.id][0]}```"

        await ctx.send(content=text)



    async def xps_inc(self, msg):
        bot = self.bot
        xps = self.xps
        user=msg.author.id
        if user not in xps:
            xps[user]=[randint(1,5),0]
        else:
            xps[user][0]+=randint(1,5)
        xp=xps[user][0]
        levelup=self.lvlup(user,xp)
        curlvl=xps[user][1]
        if levelup==1:
            user=bot.get_user(user)
            await msg.channel.send(f"Congrats {user.mention}! you just leveled up to {curlvl}")
        self.commit()


    def lvlup(self,user,xp):
        xps=self.xps
        curlvl=xps[user][1]
        nextlvl=int(xp**(1/4))
        if curlvl!=nextlvl:
            xps[user][1]+=1
            return 1
        else:
            return 0



    @commands.Cog.listener()
    async def on_message(self,msg):
        bot=self.bot
        if msg.author.bot:
            return
        await self.xps_inc(msg)



def setup(bot):
  bot.add_cog(Levelling(bot))
