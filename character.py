import json
from random import randint


class Character:
    LEVEL_UP_POINTS = 5

    def __init__(self, name: str):
        rand = randint(1, 5)
        self.stats = CharStats(hp=rand, dmg=self.LEVEL_UP_POINTS - rand)
        self.level = 1
        self.name = name

    def __str__(self):
        return f"Name: {self.name}\nLevel: {self.level}\nStats -> [{self.stats}]"

    def __repr__(self):
        return json.dumps(
            {
                "stats": self.stats.to_dict,
                "name": self.name,
                "level": self.level
            }
        )

    def upgrade(self):
        rand = randint(1, 5)
        self.stats.hp += rand
        self.stats.dmg += self.LEVEL_UP_POINTS - rand
        self.stats.luck += randint(0, 1)
        self.level += 1


class CharStats:
    def __init__(self, **kwargs):
        self.hp = kwargs.get("hp", 0)
        self.dmg = kwargs.get("dmg", 0)
        self.luck = kwargs.get("luck", 0)

    def __str__(self):
        return f"HP: {self.hp} DMG: {self.dmg} Luck: {self.luck}"

    @property
    def to_dict(self):
        return {"hp": self.hp, "dmg": self.dmg, "luck": self.luck}

