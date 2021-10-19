import discord
from discord.ext import commands



class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_ready(self):
        print("Bot online!")


    @commands.command(aliases=["purge"])
    async def clear(self, ctx, amount: int):
    	await ctx.channel.purge(limit=amount)



    @commands.command()
    async def init(self, ctx):
        await ctx.trigger_typing()
        msg= await ctx.send("```Initializing.```")
        for i in range(10):

            await msg.edit(content="```Initializing..```")

            await msg.edit(content="```Initializing...```")

            await msg.edit(content="```Initializing.```")

        await msg.edit(content="```Initializing..```")

        await msg.edit(content="```Initializing...```")

        await msg.edit(content="```Initialized successfully!```")


def setup(bot):
  bot.add_cog(Utility(bot))
