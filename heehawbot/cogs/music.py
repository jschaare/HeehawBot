import asyncio
import youtube_dl as ytdl
import discord
from discord import Embed
from discord.ext import commands
from discord.ext.commands import Bot, Cog, Context
from datetime import timedelta

YTDL_OPTS = {
    "default_search": "ytsearch",
    "format": "bestaudio/best",
    "extract_flat": "in_playlist",
}

FFMPEG_OPTS = "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"


class YoutubeVideo:
    def __init__(self, url, user) -> None:
        video = self._extract(url)
        self.stream_url = video["formats"][0]["url"]
        self.video_url = video["webpage_url"]
        self.title = video["title"]
        self.uploader = video["uploader"] if "uploader" in video else ""
        self.thumbnail = video["thumbnail"] if "thumbnail" in video else None
        self.user = user

    def _extract(self, url):
        with ytdl.YoutubeDL(YTDL_OPTS) as downloader:
            info = downloader.extract_info(url, download=False)
            if "_type" in info and info["_type"] == "playlist":
                return self._extract(info["entries"][0]["url"])
            else:
                return info

    def embed(self):
        emb = Embed(title=self.title, description=self.uploader, url=self.video_url)
        if self.thumbnail:
            emb.set_thumbnail(url=self.thumbnail)
        emb.set_footer(
            text=f"Queued by {self.user.name}", icon_url=self.user.avatar_url
        )
        return emb


class GuildMusicManager:
    def __init__(self) -> None:
        self.playlist = []
        self.playing = None
        self.volume = 1.0


async def in_voice(ctx):
    uv = ctx.author.voice
    bv = ctx.guild.voice_client
    if uv and bv and uv.channel and bv.channel and uv.channel == bv.channel:
        return True
    return False


class Music(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.managers = {}

    def _get_manager(self, guild) -> GuildMusicManager:
        if guild.id in self.managers:
            return self.managers[guild.id]
        else:
            self.managers[guild.id] = GuildMusicManager()
            return self.managers[guild.id]

    def _play(self, vc, manager, video):
        manager.playing = video
        source = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio(video.stream_url, before_options=FFMPEG_OPTS),
            volume=manager.volume,
        )

        def cleanup(err):
            if len(manager.playlist) > 0:
                next_song = manager.playlist.pop(0)
                self._play(vc, manager, next_song)
            else:
                asyncio.run_coroutine_threadsafe(vc.disconnect(), self.bot.loop)

        vc.play(source, after=cleanup)

    @commands.command(aliases=["p"])
    @commands.guild_only()
    async def play(self, ctx, *, url):
        vc = ctx.guild.voice_client
        manager = self._get_manager(ctx.guild)

        if vc and vc.channel:
            try:
                video = YoutubeVideo(url, ctx.author)
            except ytdl.DownloadError as e:
                self.bot.logger.error(f"`{type(e).__name__}: {e}`")
                return
            manager.playlist.append(video)
            msg = await ctx.send(embed=video.embed())
        else:
            if ctx.author.voice is not None and ctx.author.voice.channel is not None:
                chan = ctx.author.voice.channel
                try:
                    video = YoutubeVideo(url, ctx.author)
                except ytdl.DownloadError as e:
                    self.bot.logger.error(f"`{type(e).__name__}: {e}`")
                    return
                vc = await chan.connect()
                self._play(vc, manager, video)
                msg = await ctx.send(embed=video.embed())
            else:
                self.bot.logger.error("User must be in a voice channel")
                return

    @commands.command(aliases=["n"])
    @commands.check(in_voice)
    @commands.guild_only()
    async def skip(self, ctx):
        vc = ctx.guild.voice_client
        vc.stop()

    @commands.command()
    @commands.check(in_voice)
    @commands.guild_only()
    async def clear(self, ctx):
        manager = self._get_manager(ctx.guild)
        manager.playlist = []

        vc = ctx.guild.voice_client
        vc.stop()

    @commands.command()
    @commands.guild_only()
    async def queue(self, ctx):
        manager = self._get_manager(ctx.guild)
        if len(manager.playlist) > 0:
            msg = "Queue:\n"
            for i, song in enumerate(manager.playlist):
                msg += f"{i+1}: {song.title}\n"
            await ctx.send(msg)
        else:
            await ctx.send("No songs in queue...")


def setup(bot):
    bot.add_cog(Music(bot))
