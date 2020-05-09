from discord.ext import commands
from discord import Embed
from bot.bot import Bot
from bot.api.osrs.player import Player
from bot.api.osrs.skills import Skill

def get_player_embed(p : Player):
    pe = Embed(colour=0x00FF00, title=p.username) \
        .set_author(name="OSRS Highscores") \
        .add_field(name="***Rank***", value=p.rank) \
        .add_field(name="***Total Level***", value=p.total_level) \
        .add_field(name="***Total XP***", value=p.total_xp)

    skill_name_string = ""
    #skill_rank_string = ""
    skill_level_string = ""
    skill_xp_string = ""
    for s in p.skills:
        sk = p.skills[s]
        skill_name_string  += f"**{sk.get_name()}**\n"
        #skill_rank_string  += f"{sk.get_rank()}\n"
        skill_level_string += f"{sk.get_level()}\n"
        skill_xp_string    += f"{sk.get_xp()}\n"
    pe.add_field(name="***Skill***", value=skill_name_string)
    #pe.add_field(name="***Rank***", value=skill_rank_string)
    pe.add_field(name="***Level***", value=skill_level_string)
    pe.add_field(name="***XP***", value=skill_xp_string)

    return pe

class Osrs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name='osrs', invoke_without_command=True)
    async def _osrs(self, ctx):
        await ctx.send("Nice.")

    @_osrs.command()
    async def highscore(self, ctx, username : str, account_type=None):
        try:
            user_player = Player(username, account_type)
        except Exception as e:
            await ctx.send(f"`{type(e).__name__}: {e}`")
        else:
            await ctx.send(embed=get_player_embed(user_player))

def setup(bot):
    bot.add_cog(Osrs(bot))