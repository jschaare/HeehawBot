from discord import Option
from discord.ext import commands
from discord.ext.commands import Cog

from heehawbot.managers.audio.manager import AudioManager
from heehawbot.managers.audio.queue import QueueEmbed
from heehawbot.utils import config

guild_ids = config.get_config()["guilds"]


class Music(Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.manager: AudioManager = self.bot.audio_manager

    # @commands.command(aliases=["p"])
    @commands.slash_command(guild_ids=guild_ids, description="play a song")
    @commands.guild_only()
    async def play(self, ctx, *, query: Option(str, "Youtube search or url")):
        embed = await self.manager.play(
            ctx.guild.id, ctx.author.id, ctx.channel.id, query
        )
        msg = await ctx.respond(embed=embed)
        await msg.delete_original_message(delay=5)

    # @commands.command(aliases=["n"])
    @commands.slash_command(guild_ids=guild_ids, description="skip a song")
    @commands.guild_only()
    async def skip(self, ctx):
        await self.manager.skip(ctx.guild.id, ctx.author.id, ctx.channel.id)
        msg = await ctx.respond("skipped")
        await msg.delete_original_message(delay=1)

    @commands.slash_command(guild_ids=guild_ids, description="clear queue")
    @commands.guild_only()
    async def clear(self, ctx):
        await self.manager.clear(ctx.guild.id, ctx.author.id, ctx.channel.id)
        msg = await ctx.respond("cleared queue")
        await msg.delete_original_message(delay=1)

    @commands.slash_command(guild_ids=guild_ids, description="show song queue")
    @commands.guild_only()
    async def queue(self, ctx):
        q = await self.manager.queue(ctx.guild.id, ctx.author.id, ctx.channel.id)

        await ctx.respond(embed=QueueEmbed(q).embed(), ephemeral=True)

    @commands.slash_command(guild_ids=guild_ids, description="kill music player")
    @commands.guild_only()
    async def kill(self, ctx):
        await self.manager.kill_player(ctx.guild.id, ctx.author.id, ctx.channel.id)
        msg = await ctx.respond("killed music player")
        await msg.delete_original_message(delay=1)


def setup(bot):
    bot.add_cog(Music(bot))
