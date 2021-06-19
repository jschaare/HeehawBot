import datetime
import logging
from discord import Embed, Color
from discord.ext import commands

from heehawbot.utils.config import get_config


class DiscordLogHandler(logging.Handler):
    def __init__(self, bot: commands.Bot, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot = bot
        self.logging_channel_id = get_config()["log_channel"]
        self.channel = None

        self._set_channel()

    def _set_channel(self):
        self.channel = self.bot.get_channel(self.logging_channel_id)

    def emit(self, record):
        if not self.bot.loop.is_running():
            return

        embed = (
            Embed(colour=Color.red(), title=record.levelname.title())
            .add_field(name="***MSG***", value=record.msg, inline=False)
            .add_field(name="***FUNC***", value=record.funcName, inline=False)
            .add_field(name="***FILE***", value=record.filename, inline=False)
            .add_field(name="***LINE***", value=record.lineno, inline=False)
        )
        embed.timestamp = datetime.datetime.utcnow()

        if self.channel is None:
            self._set_channel()
        self.bot.loop.create_task(self.channel.send(embed=embed))
