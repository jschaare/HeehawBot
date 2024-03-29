from discord import Embed
from discord.ext.commands import Bot, Cog, Context
from discord.commands import SlashCommandGroup
from osrs.highscores import Player

from heehawbot.utils import config

guild_ids = config.get_config()["guilds"]


class Osrs(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    _osrs = SlashCommandGroup("osrs", "osrs commands", guild_ids=guild_ids)

    @_osrs.command()
    async def highscore(self, ctx: Context, username: str):
        try:
            p = Player(username)
            embed = self._player_embed(p)
        except Exception as e:
            self.bot.logger.error(f"`{type(e).__name__}: {e}`")
        else:
            await ctx.respond(embed=embed)

    def _player_embed(self, p: Player):
        # TODO: generate image of highscores rather than stupid text
        embed = (
            Embed(colour=0x00FF00, title=p.username)
            .set_author(name="OSRS Highscores")
            .set_thumbnail(url="https://i.imgur.com/jzxVYS0.png")
            .add_field(name="***Rank***", value=p.rank)
            .add_field(name="***Total Level***", value=p.total_level)
            .add_field(name="***Total XP***", value=p.total_xp)
        )

        skill_name = ""
        skill_level = ""
        skill_xp = ""
        for s in p.skills:
            sk = p.skills[s]
            skill_name += f"**{sk.name}**\n"
            skill_level += f"{sk.level}\n"
            skill_xp += f"{sk.xp}\n"
        embed.add_field(name="***Skill***", value=skill_name)
        embed.add_field(name="***Level***", value=skill_level)
        embed.add_field(name="***XP***", value=skill_xp)
        return embed


def setup(bot):
    bot.add_cog(Osrs(bot))
