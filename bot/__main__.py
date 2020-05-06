import os
from dotenv import load_dotenv
from bot.bot import Bot

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = Bot(command_prefix="~")
bot.load_extension("bot.cogs.admin")
bot.load_extension("bot.cogs.example")

bot.run(TOKEN)