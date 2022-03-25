import asyncio
import youtube_dl as ytdl
import discord
from discord import Embed, Option
from discord.ext import commands
from discord.ext.commands import Cog, Context

from heehawbot.managers.audio import AudioManager, GuildPlayer
from heehawbot.utils import config

guild_ids = config.get_config()["guilds"]


class NewMusic(Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.manager: AudioManager = self.bot.audio_manager

    # @commands.command(aliases=["p"])
    @commands.slash_command(guild_ids=guild_ids, description="play a song")
    @commands.guild_only()
    async def play(self, ctx: Context, *, query: Option(str, "Youtube search or url")):
        embed = await self.manager.play(
            ctx.guild.id, ctx.author.id, ctx.channel.id, query
        )
        msg = await ctx.respond(embed=embed)
        await msg.delete_original_message(delay=5)

    # @commands.command(aliases=["n"])
    @commands.slash_command(guild_ids=guild_ids, description="skip a song")
    @commands.guild_only()
    async def skip(self, ctx):
        await self.manager.skip(ctx.guild.id, ctx.author.id)
        msg = await ctx.respond("skipped")
        await msg.delete_original_message(delay=1)


def setup(bot):
    bot.add_cog(NewMusic(bot))
