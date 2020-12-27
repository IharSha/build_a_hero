from random import randint

from django.contrib.auth.models import User
from django.db import models, transaction


class Character(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=64, null=False)
    level = models.PositiveSmallIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def level_up(self):
        self.level += 1
        attrs, _ = CharacterAttributes.objects.get_or_create(character=self)
        with transaction.atomic():
            attrs.upgrade()
            self.save()

    def __str__(self):
        return f"{self.name}, level {self.level}"

    class Meta:
        unique_together = ['user', 'name']


class CharacterAttributes(models.Model):
    LEVEL_UP_POINTS = 25

    character = models.OneToOneField(
        Character,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    max_hp = models.IntegerField(default=10)
    hp = models.IntegerField(default=10)
    dmg = models.IntegerField(default=1)
    luck = models.IntegerField(default=1)

    def upgrade(self):
        hp_increase = randint(1, 24)
        self.max_hp += hp_increase
        self.hp += hp_increase
        self.dmg += self.LEVEL_UP_POINTS - hp_increase
        self.luck += randint(0, 1)
        self.save()

    def __str__(self):
        return f"HP {self.hp}/{self.max_hp}, DMG {self.dmg}, Luck {self.luck}"

    class Meta:
        verbose_name_plural = "Character Attributes"
