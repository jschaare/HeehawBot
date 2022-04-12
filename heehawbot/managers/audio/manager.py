import discord

from ..audio.player import GuildPlayer, GuildPlayerView


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
            song = await player.put_song(query, member)
            if song is None:
                return discord.Embed(description="Could not queue the song... Sorry!")
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

    async def skip(self, guild_id, user_id, tchannel_id):
        guild: discord.Guild = self.bot.get_guild(guild_id)
        if not guild:
            return

        member = guild.get_member(user_id)
        if not member:
            return

        vclient = guild.voice_client
        if not vclient or not vclient.is_connected():
            return

        vchannel = member.voice.channel
        if not vchannel:
            return

        tchannel = guild.get_channel(tchannel_id)
        if not tchannel:
            return

        if isinstance(tchannel, discord.TextChannel):
            player = self.get_player(guild, tchannel)
            await player.skip()
            return

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
            await player.clear_queue()
            return

    async def kill_player(self, guild_id, user_id, tchannel_id):
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
            player = None
            del self.players[guild_id]
