from discord.ext import commands
from bot.bot import Bot

from enum import Enum
import requests

#TODO move to other file?
class Skills(Enum):
    Attack = 0
    Defence = 1
    Strength = 2
    Hitpoints = 3
    Ranged = 4
    Prayer = 5
    Magic = 6
    Cooking = 7
    Woodcutting = 8
    Fletching = 9
    Fishing = 10
    Firemaking = 11
    Crafting = 12
    Smithing = 13
    Mining = 14
    Herblore = 15
    Agility = 16
    Thieving = 17
    Slayer = 18
    Farming = 19
    Runecrafting = 20
    Hunter = 21
    Construction = 22

class Skill(object):
    def __init__(self, name, rank, level, xp):
        self.name = name
        self.rank = rank
        self.level = level
        self.xp = xp

    def get_name():
        return self.name

    def get_rank():
        return self.rank
    
    def get_level():
        return self.level
    
    def get_xp():
        return self.xp

    def set_rank(self, rank):
        self.rank = rank

    def set_level(self, level):
        self.level = level
    
    def set_xp(self, xp):
        self.xp = xp
    
    def __str__(self):
        return f"{self.name}\tRank: {self.rank}\tLevel: {self.level}\tXP: {self.xp}"

class OsrsPlayer(object):
    def __init__(self, username, account_type=None):
        self.username = username
        self.account_type = account_type
        if account_type == None:
            account_type_str = ""
        else:
            account_type_str = f"_{account_type}"
        self.url = f"https://secure.runescape.com/m=hiscore_oldschool{account_type_str}/index_lite.ws?player={username}"
        self.rank = -1
        self.total_level = -1
        self.total_xp = -1
        self.skills = {}
        self.fetch_data()

    def fetch_data(self):
        self.api_payload = self._get_highscores()
        self._parse_payload(self.api_payload)

    def _get_highscores(self):
        try:
            payload = requests.get(self.url)
            payload.raise_for_status()
        except Exception as e:
            raise Exception
        return payload.text.split("\n")

    def _parse_payload(self, payload):
        top_stats = payload[0].split(",")
        self.rank, self.total_level, self.total_xp = top_stats[0], top_stats[1], top_stats[2]

        position = 1
        for skill in Skills:
            skill_line = payload[position].split(",")
            if skill not in self.skills:
                self.skills[skill] = Skill(skill.name, skill_line[0], skill_line[1], skill_line[2])
            position += 1

    def __str__(self):
        return (
            "```" +
            f"Name: {self.username}\n" +
            f"Rank: {self.rank}\n" +
            f"Total Level: {self.total_level} Total XP: {self.total_xp}\n" +
            "\n".join([str(self.skills[skill]) for skill in self.skills]) +
            "```"
        )


class Osrs(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.group(name='osrs', invoke_without_command=True)
    async def _osrs(self, ctx):
        await ctx.send("Nice.")

    @_osrs.command()
    async def highscore(self, ctx, username : str, account_type=None):
        try:
            player = OsrsPlayer(username, account_type)
        except Exception as e:
            print('fuuu')
        else:
            await ctx.send(player)

def setup(bot):
    bot.add_cog(Osrs(bot))