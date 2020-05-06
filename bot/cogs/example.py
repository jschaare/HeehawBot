from discord.ext import commands
from bot.bot import Bot

class Example(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def tryme(self, ctx):
        response = "Nice, Ayy lmao"
        await ctx.send(response)

    @commands.command()
    async def whoami(self, ctx):
        response = f"Hey there, {ctx.author.display_name}!"
        await ctx.send(response)

def setup(bot):
    bot.add_cog(Example(bot))