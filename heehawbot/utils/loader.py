from typing import List
from discord.ext.commands.bot import Bot


def load_cogs(bot: Bot, coglist: List):
    for cog in coglist:
        bot.load_extension(cog)
