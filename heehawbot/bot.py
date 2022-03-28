import datetime
import logging
from discord.ext import commands
from heehawbot.managers.audio.manager import AudioManager
from heehawbot.utils.logger import DiscordLogHandler


class HeehawBot(commands.Bot):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(DiscordLogHandler(self))
        self.audio_manager = AudioManager(self)

    """
    def add_cog(self, cog):
        super().add_cog(cog)
        self.logger.info(f"Cog loaded: {cog.qualified_name}")
    """

    async def on_ready(self):
        if not hasattr(self, "uptime"):
            self.uptime = datetime.datetime.utcnow()
        self.logger.info(f"Ready: {self.user} (ID: {self.user.id})")
