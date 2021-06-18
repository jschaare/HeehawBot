import os
from bot.utils import config
from bot.bot import Bot

cfg = config.get_config()

TOKEN = cfg["discord_token"]

bot = Bot(command_prefix="~")
bot.load_extension("bot.cogs.admin")
bot.load_extension("bot.cogs.example")
bot.load_extension("bot.cogs.osrs")
bot.load_extension("bot.cogs.events")
bot.load_extension("bot.cogs.twitch")

bot.run(TOKEN)