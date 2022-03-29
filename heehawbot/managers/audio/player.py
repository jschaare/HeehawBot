import asyncio
import youtube_dl
import discord

from ..audio.ytdlsource import YTDLSource
from ..audio.queue import QueueEmbed

YTDL_OPTS = {
    "format": "webm[abr>0]/bestaudio/best",
    "prefer_ffmpeg": True,
    "ignoreerrors": True,
    "default_search": "ytsearch",
    "source_address": "0.0.0.0",
}


class GuildPlayerButton(discord.ui.Button):
    def __init__(self, cb, label, style=discord.ButtonStyle.primary):
        self.cb = cb
        super().__init__(label=label, style=style)

    async def callback(self, interaction: discord.Interaction):
        if (
            not interaction.user
            and not interaction.guild
            and not interaction.channel_id
        ):
            return
        return await self.cb(self, interaction)


class GuildPlayerView(discord.ui.View):
    def __init__(self, manager, guild):
        super().__init__(timeout=None)
        self.manager = manager
        self.guild = guild

    async def load(self):
        self.clear_items()
        self.add_item(GuildPlayerButton(self.skip, label="skip"))
        self.add_item(
            GuildPlayerButton(self.clear, label="clear", style=discord.ButtonStyle.red)
        )
        self.add_item(
            GuildPlayerButton(
                self.queue, label="queue", style=discord.ButtonStyle.green
            )
        )

    async def skip(self, button: GuildPlayerButton, interaction: discord.Interaction):
        await self.manager.skip(
            interaction.guild_id, interaction.user.id, interaction.channel_id
        )

    async def clear(self, button: GuildPlayerButton, interaction: discord.Interaction):
        await self.manager.clear(
            interaction.guild_id, interaction.user.id, interaction.channel_id
        )

    async def queue(self, button: GuildPlayerButton, interaction: discord.Interaction):
        q = await self.manager.queue(
            interaction.guild_id, interaction.user.id, interaction.channel_id
        )
        await interaction.response.send_message(
            embed=QueueEmbed(q).embed(), ephemeral=True
        )


class GuildPlayer:
    def __init__(
        self,
        bot,
        guild: discord.Guild,
        channel: discord.TextChannel,
        view: GuildPlayerView,
    ):
        self.bot = bot
        self.guild = guild
        self.tchan = channel
        self.ytdl = youtube_dl.YoutubeDL(YTDL_OPTS)
        self.vclient = self.guild.voice_client
        self.loop = self.vclient.loop

        self.volume = 1.0
        self.playlist = asyncio.Queue()
        self.playlist_helper = []
        self.next = asyncio.Event()
        self.playing_now = None
        self.playing_last = None

        self.view = view
        self.view_msg = None
        self.audio_player = self.loop.create_task(self.play_loop())

    def play_finished(self, err):
        return self.loop.call_soon_threadsafe(self.next.set)

    async def cleanup(self):
        print("cleaning up")
        await self.cleanup_view_msg()
        self.vclient.stop()
        for _ in range(self.playlist.qsize()):
            self.playlist.get_nowait()
            self.playlist.task_done()
        self.playlist_helper.clear()
        self.vclient.cleanup()
        await self.vclient.disconnect()

    async def play_loop(self):
        await self.bot.wait_until_ready()

        while not self.bot.is_closed():
            self.next.clear()

            src = await self.get_song()
            self.playing_last = self.playing_now
            self.playing_now = src

            self.vclient = self.guild.voice_client
            if not self.vclient:
                print("something goofed, cleaning up")
                return await self.cleanup()

            if src and self.vclient:
                print("playing")
                self.vclient.play(src, after=self.play_finished)
                await self.update_view_msg()

            await self.next.wait()

            # TODO: maybe try and update play message when out of songs
            """ if self.playlist.empty():
                print("playlist empty")
                self.playing_last = self.playing_now
                self.playing_now = None
                print("some cleanup")
                await self.cleanup_view_msg() """

    async def update_view_msg(self):
        print("updating view msg")
        await self.cleanup_view_msg()

        if self.view:
            await self.view.load()
        self.view_msg = await self.tchan.send(
            embed=self.playing_now.embed(is_playing=True), view=self.view
        )

    async def cleanup_view_msg(self):
        if self.view_msg:
            if self.playing_last and self.view_msg:
                await self.view_msg.edit(embed=self.playing_last.embed(), view=None)

    async def put_song(self, query):
        try:
            ytdlsrc = await YTDLSource.from_query(
                self.ytdl, query, loop=self.loop, stream=True
            )
        except youtube_dl.DownloadError as e:
            self.bot.logger.error(f"`{type(e).__name__}: {e}`")
            return
        if ytdlsrc is None:
            return
        await self.playlist.put(ytdlsrc)
        self.playlist_helper.append({"title": ytdlsrc.title, "url": ytdlsrc.webpage})
        return ytdlsrc

    async def get_song(self, has_timeout=True):
        src = None
        if has_timeout:
            # timeout causes bot to die, not sure why lol
            """
            async with timeout(300):
                print("waiting")
                src = await self.playlist.get()
            """
            src = await self.playlist.get()
        else:
            src = self.playlist.get_nowait()
        self.playlist_helper.pop(0)
        return src

    async def get_queue(self):
        return self.playlist_helper[:10]

    async def clear_queue(self):
        if self.vclient.is_playing():
            self.vclient.stop()
        try:
            for _ in range(self.playlist.qsize()):
                self.playlist.get_nowait()
                self.playlist.task_done()
        except asyncio.QueueEmpty:
            pass
        self.playlist_helper.clear()

    async def skip(self):
        if self.vclient.is_playing():
            self.vclient.stop()
