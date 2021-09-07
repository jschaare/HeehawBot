import discord
from heehawbot.bot import HeehawBot
from heehawbot.utils import config
from heehawbot.utils.loader import load_cogs

cfg = config.get_config()

TOKEN = cfg["discord_token"]

coglist = [
    "heehawbot.cogs.admin",
    "heehawbot.cogs.poll",
    "heehawbot.cogs.mtg",
    "heehawbot.cogs.osrs",
    "heehawbot.cogs.music",
]

bot = HeehawBot(command_prefix="-", intents=discord.Intents.all())
load_cogs(bot, coglist)

bot.run(TOKEN)
