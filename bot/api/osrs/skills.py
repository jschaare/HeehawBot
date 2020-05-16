from enum import Enum

class SkillsList(Enum):
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

    def get_name(self):
        return self.name

    def get_rank(self):
        return self.rank
    
    def get_level(self):
        return self.level
    
    def get_xp(self):
        return self.xp

    def set_rank(self, rank):
        self.rank = rank

    def set_level(self, level):
        self.level = level
    
    def set_xp(self, xp):
        self.xp = xp
    
    def __str__(self):
        return f"{self.name}\tRank: {self.rank}\tLevel: {self.level}\tXP: {self.xp}"