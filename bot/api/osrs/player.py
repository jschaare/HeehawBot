from enum import Enum
import requests

from bot.api.osrs.skills import Skill, SkillsList

class Player(object):
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
        for skill in SkillsList:
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