from random import randint
from datetime import timedelta

from django.contrib.auth.models import User
from django.db import models, transaction
from django.utils import timezone

from wwwhero.exceptions import LevelUpCooldownError, MaxLevelError


class Character(models.Model):
    MAX_LEVEL = 20

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=64, null=False)
    level = models.PositiveSmallIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def level_up(self):
        self.level += 1
        attrs, _ = CharacterAttributes.objects.get_or_create(character=self)

        cooldown = CharacterCooldown.objects.filter(
            character=self,
            type=CharacterCooldown.Type.LEVEL,
        ).first()
        if cooldown and cooldown.until > timezone.now():
            raise LevelUpCooldownError

        if self.level > self.MAX_LEVEL:
            raise MaxLevelError

        with transaction.atomic():
            CharacterCooldown.objects.update_or_create(
                character=self,
                type=CharacterCooldown.Type.LEVEL,
                defaults={
                    'until': timezone.now() + timedelta(seconds=2 ** self.level)
                }
            )
            attrs.upgrade()
            self.save()

    def __str__(self):
        return f"{self.user}, {self.name}, level {self.level}"

    class Meta:
        unique_together = ['user', 'name']


class CharacterSelection(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    character = models.OneToOneField(Character, on_delete=models.CASCADE)


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
        return f"Character name: {self.character.name}," \
               f" HP {self.hp}/{self.max_hp}, DMG {self.dmg}, Luck {self.luck}"

    class Meta:
        verbose_name_plural = "Character attributes"


class CharacterCooldown(models.Model):
    class Type(models.TextChoices):
        LEVEL = "Level"
        SKILL = "Skill"

    type = models.CharField(
        max_length=5,
        choices=Type.choices,
        default=Type.LEVEL,
        blank=False
    )
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    until = models.DateTimeField()

    class Meta:
        unique_together = ['type', 'character']


class LocationType(models.Model):
    name = models.CharField(max_length=32, primary_key=True)

    def __str__(self):
        return self.name


class Location(models.Model):
    name = models.CharField(max_length=64, unique=True)
    image = models.ImageField(upload_to='bg/location', blank=True)
    min_level = models.PositiveSmallIntegerField(default=1)
    is_active = models.BooleanField(default=False)
    type = models.ForeignKey(LocationType, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class CharacterLocation(models.Model):
    character = models.OneToOneField(
        Character,
        on_delete=models.CASCADE,
        primary_key=True
    )
    location = models.ForeignKey(Location, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.location)


class UserVisit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    view = models.PositiveSmallIntegerField(default=0)
    url = models.CharField(null=False, max_length=200)
    method = models.CharField(max_length=8)

    def __str__(self):
        if len(self.url) > 10:
            url = self.url[:10] + '...'
        else:
            url = self.url

        return f"{self.user.username}, {url}, {self.method}, {self.view} views"

    class Meta:
        unique_together = ['user', 'url', 'method']
