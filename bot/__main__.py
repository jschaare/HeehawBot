import os
import json
from bot.bot import Bot

with open("config.json") as f:
    cfg = json.load(f)

TOKEN = cfg["discord_token"]

bot = Bot(command_prefix="~")
bot.load_extension("bot.cogs.admin")
bot.load_extension("bot.cogs.example")
bot.load_extension("bot.cogs.osrs")
bot.load_extension("bot.cogs.events")

bot.run(TOKEN)