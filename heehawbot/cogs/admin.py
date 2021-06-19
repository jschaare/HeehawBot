from discord.ext import commands
from discord.ext.commands import Bot, Cog, Context
import inspect


class Admin(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.command(hidden=True)
    @commands.is_owner()
    async def shutdown(self, ctx: Context):
        try:
            self.bot.logger.info("Shutting down...")
            await self.bot.close()
        except Exception as e:
            self.bot.logger.error(f"`{type(e).__name__}: {e}`")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def load(self, ctx: Context, *, module: str):
        try:
            self.bot.load_extension(module)
        except Exception as e:
            self.bot.logger.error(f"`{type(e).__name__}: {e}`")
        else:
            self.bot.logger.info(f"Successfully loaded cog... `{module}`")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def unload(self, ctx: Context, *, module: str):
        try:
            self.bot.unload_extension(module)
        except Exception as e:
            self.bot.logger.error(f"`{type(e).__name__}: {e}`")
        else:
            self.bot.logger.info(f"Successfully unloaded cog... `{module}`")

    @commands.group(name="reload", hidden=True, invoke_without_command=True)
    @commands.is_owner()
    async def _reload(self, ctx: Context, *, module: str):
        try:
            self.bot.reload_extension(module)
        except Exception as e:
            self.bot.logger.error(f"`{type(e).__name__}: {e}`")
        else:
            self.bot.logger.info(f"Successfully reloaded cog... `{module}`")

    @_reload.command(name="all", hidden=True)
    @commands.is_owner()
    async def _reload_all(self, ctx: Context):
        try:
            cogs = self.bot.cogs
            for cog in cogs:
                # TODO find less hacky way to do this
                cog_name = str(inspect.getmodule(cogs[cog]).__name__)
                self.bot.reload_extension(cog_name)
        except Exception as e:
            self.bot.logger.error(f"`{type(e).__name__}: {e}`")
        else:
            self.bot.logger.info("Reloaded all cogs...")


def setup(bot):
    bot.add_cog(Admin(bot))
