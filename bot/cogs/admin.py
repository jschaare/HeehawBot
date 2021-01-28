from discord.ext import commands
from bot.bot import Bot
import inspect

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
    @commands.is_owner()
    async def shutdown(self, ctx):
        try:
            await ctx.send("Shutting down...")
            await self.bot.close()
        except Exception as e:
            await ctx.send(f"`{type(e).__name__}: {e}`")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def load(self, ctx, *, module : str):
        try:
            self.bot.load_extension(module)
        except Exception as e:
            await ctx.send(f"`{type(e).__name__}: {e}`")
        else:
            await ctx.send(f"Successfully loaded cog... `{module}`")
    
    @commands.command(hidden=True)
    @commands.is_owner()
    async def unload(self, ctx, *, module : str):
        try:
            self.bot.unload_extension(module)
        except Exception as e:
            await ctx.send(f"`{type(e).__name__}: {e}`")
        else:
            await ctx.send(f"Successfully unloaded cog... `{module}`")

    @commands.group(name='reload', hidden=True, invoke_without_command=True)
    @commands.is_owner()
    async def _reload(self, ctx, *, module : str):
        try:
            self.bot.reload_extension(module)
        except Exception as e:
            await ctx.send(f"`{type(e).__name__}: {e}`")
        else:
            await ctx.send(f"Successfully reloaded cog... `{module}`")

    @_reload.command(name='all', hidden=True)
    @commands.is_owner()
    async def _reload_all(self, ctx):
        try:
            cogs = self.bot.cogs
            for cog in cogs:
                #TODO find less hacky way to do this
                cog_name=str(inspect.getmodule(cogs[cog]).__name__)
                self.bot.reload_extension(cog_name)
        except Exception as e:
            await ctx.send(f"`{type(e).__name__}: {e}`")
        else:
            await ctx.send("Reloaded all cogs...")

def setup(bot):
    bot.add_cog(Admin(bot))