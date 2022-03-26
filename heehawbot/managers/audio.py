from async_timeout import timeout
import asyncio
import subprocess
import youtube_dl
import discord
from discord import Embed
from functools import wraps

YTDL_OPTS = {
    "format": "webm[abr>0]/bestaudio/best",
    "prefer_ffmpeg": True,
    "ignoreerrors": True,
    "default_search": "ytsearch",
    "source_address": "0.0.0.0",  # ipv6 addresses cause issues sometimes
}

FFMPEG_OPTS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn",
    "stderr": subprocess.PIPE,
}


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=1.0):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get("title")
        self.url = data.get("url")
        self.uploader = data.get("uploader", "")
        self.thumbnail = data.get("thumbnail")

    @classmethod
    async def from_query(cls, ytdl, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(
            None, lambda: ytdl.extract_info(url, download=not stream)
        )

        if "entries" in data:
            # Takes the first item from a playlist
            data = data["entries"][0]

        filename = data["url"] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **FFMPEG_OPTS), data=data)

    def embed(self, is_playing=False):
        if is_playing:
            colour = 0x00FF00
        else:
            colour = 0x0
        emb = Embed(
            title=self.title, description=self.uploader, url=self.url, colour=colour
        )
        if self.thumbnail:
            emb.set_thumbnail(url=self.thumbnail)
        return emb


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
        await self.manager.skip(interaction.guild_id, interaction.user.id)

    async def clear(self, button: GuildPlayerButton, interaction: discord.Interaction):
        await self.manager.clear(
            interaction.guild_id, interaction.user.id, interaction.channel_id
        )

    async def queue(self, button: GuildPlayerButton, interaction: discord.Interaction):
        q = await self.manager.queue(
            interaction.guild_id, interaction.user.id, interaction.channel_id
        )
        # TODO: MAKE QUEUE EMBED OBJ
        song_str = "Songs:\n"
        if len(q) > 0:
            for n in range(len(q)):
                i = q[n]
                url = i.get("url")
                title = i.get("title")
                if len(title) > 50:
                    title = title[:47] + "..."
                song_str += f"{n}. [{title}]({url})\n"
        else:
            song_str += "Nothing in queue!"
        e = Embed(title="Coming Up", description=song_str)
        await interaction.response.send_message(embed=e, ephemeral=True)


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
                return await self.cleanup()

            if src and self.vclient:
                self.vclient.play(src, after=self.play_finished)
                await self.update_view_msg()

            await self.next.wait()

            if self.playlist.empty():
                await self.cleanup()

    async def update_view_msg(self):
        if self.view_msg:
            if self.playing_last:
                await self.view_msg.edit(embed=self.playing_last.embed(), view=None)
        await self.view.load()
        self.view_msg = await self.tchan.send(
            embed=self.playing_now.embed(is_playing=True), view=self.view
        )

    async def cleanup_view_msg(self):
        if self.view_msg:
            await self.view_msg.delete()

    async def put_song(self, query):
        try:
            ytdlsrc = await YTDLSource.from_query(
                self.ytdl, query, loop=self.loop, stream=True
            )
        except youtube_dl.DownloadError as e:
            self.bot.logger.error(f"`{type(e).__name__}: {e}`")
            return
        await self.playlist.put(ytdlsrc)
        self.playlist_helper.append({"title": ytdlsrc.title, "url": ytdlsrc.url})
        return ytdlsrc

    async def get_song(self, has_timeout=True):
        src = None
        if has_timeout:
            async with timeout(300):
                src = await self.playlist.get()
        else:
            src = self.playlist.get_nowait()
        self.playlist_helper.pop(0)
        return src

    async def get_queue(self):
        """q = []
        count = 0
        for song in self.playlist_helper:
            q.append({"title": song.title, "url": song.url})
            count += 1
            if count >= 10:
                return q
        return q"""
        return self.playlist_helper[:10]


class AudioManager:
    def __init__(self, bot):
        self.bot = bot
        self.players = {}

    def get_player(
        self, guild: discord.Guild, channel: discord.TextChannel
    ) -> GuildPlayer:
        if guild.id in self.players:
            return self.players[guild.id]

        view = GuildPlayerView(self, guild)
        player = GuildPlayer(self.bot, guild, channel, view)
        self.players[guild.id] = player
        return player

    async def join(self, guild: discord.Guild, vchannel: discord.VoiceChannel):
        vclient: discord.VoiceClient = guild.voice_client
        try:
            vclient = await vchannel.connect()
        except discord.ClientException:
            await vclient.move_to(vchannel)
        return vclient

    async def play(self, guild_id, user_id, tchannel_id, query):
        # TODO: cleanup
        guild: discord.Guild = self.bot.get_guild(guild_id)
        if not guild:
            return

        member = guild.get_member(user_id)
        if not member:
            return

        vchannel = member.voice.channel
        if not vchannel:
            return

        vclient = await self.join(guild, vchannel)
        if not vclient:
            return

        tchannel = guild.get_channel(tchannel_id)
        if not tchannel:
            return

        if isinstance(tchannel, discord.TextChannel):
            player = self.get_player(guild, tchannel)
            song = await player.put_song(query)
            return song.embed()

    async def queue(self, guild_id, user_id, tchannel_id):
        guild: discord.Guild = self.bot.get_guild(guild_id)
        if not guild:
            return

        member = guild.get_member(user_id)
        if not member:
            return

        tchannel = guild.get_channel(tchannel_id)
        if not tchannel:
            return

        if isinstance(tchannel, discord.TextChannel):
            player = self.get_player(guild, tchannel)
            return await player.get_queue()

    async def skip(self, guild_id, user_id):
        guild: discord.Guild = self.bot.get_guild(guild_id)
        if not guild:
            return

        vclient = guild.voice_client
        if not vclient or not vclient.is_connected():
            return

        if vclient.is_playing():
            vclient.stop()

    async def clear(self, guild_id, user_id, tchannel_id):
        guild: discord.Guild = self.bot.get_guild(guild_id)
        if not guild:
            return

        member = guild.get_member(user_id)
        if not member:
            return

        vchannel = member.voice.channel
        if not vchannel:
            return

        tchannel = guild.get_channel(tchannel_id)
        if not tchannel:
            return

        if isinstance(tchannel, discord.TextChannel):
            player = self.get_player(guild, tchannel)
            await player.cleanup()
            return
