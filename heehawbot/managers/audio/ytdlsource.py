import asyncio
import subprocess
import discord
from discord import Embed
import youtube_dl

FFMPEG_OPTS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn",
    "stderr": subprocess.PIPE,
}


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=1.0, user=None):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get("title")
        self.url = data.get("url")
        self.webpage = data.get("webpage_url")
        self.uploader = data.get("uploader", "")
        self.thumbnail = data.get("thumbnail")
        self.user = user

    @classmethod
    async def from_query(cls, ytdl, url, *, loop=None, stream=False, user: discord.Member=None):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(
            None, lambda: ytdl.extract_info(url, download=not stream)
        )

        if data is None:
            raise youtube_dl.DownloadError("could not download")

        if "entries" in data:
            data = data["entries"][0]

        filename = data["url"] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **FFMPEG_OPTS), data=data, user=user)

    def embed(self, is_playing=False):
        if is_playing:
            colour = 0x00FF00
        else:
            colour = 0x0
        emb = Embed(
            title=self.title, description=self.uploader, url=self.webpage, colour=colour
        )
        if self.thumbnail:
            emb.set_thumbnail(url=self.thumbnail)
        if self.user:
            emb.set_footer(
                text=f"Queued by {self.user.display_name}", icon_url=self.user.display_avatar.url
            )
        return emb
