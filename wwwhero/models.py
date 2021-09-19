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

            inv = Inventory.objects.get(character=self)
            inv.max_space += 1
            inv.save(update_fields=["max_space"])

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
    class Type(models.IntegerChoices):
        LEVEL = 1, "Level"
        SKILL = 2, "Skill"
        SEARCH = 3, "Search"

    type = models.PositiveSmallIntegerField(
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


class ItemBlueprint(models.Model):
    class ItemType(models.IntegerChoices):
        ARMOR = 1, "Armor"
        JUNK = 2, "Junk"
        GOLD = 3, "Gold"
        QUEST = 4, "Quest"
        WEAPON = 5, "Weapon"

    class SlotType(models.IntegerChoices):
        HEAD = 1, "Head"
        BREAST = 2, "Breast"
        LEGS = 3, "Legs"
        LEFT = 4, "Left arm"
        RIGHT = 5, "Right arm"
        BOOTS = 6, "Boots"
        INVENTORY = 7, "Inventory"

    item_type = models.PositiveSmallIntegerField(choices=ItemType.choices, blank=False)
    slot_type = models.PositiveSmallIntegerField(choices=SlotType.choices, blank=False)
    name = models.CharField(max_length=32, unique=True)
    description = models.CharField(max_length=512, blank=True)
    is_consumable = models.BooleanField(default=False)
    is_stackable = models.BooleanField(default=False)
    is_droppable = models.BooleanField(default=False)
    base_cost = models.PositiveSmallIntegerField(default=1)

    def __str__(self):
        return f"{self.name} ({self.get_item_type_display()})"


class Inventory(models.Model):
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    max_space = models.PositiveSmallIntegerField(default=20)

    def __str__(self):
        return f"{self.character}'s inventory"


class Item(models.Model):
    class Rarity(models.IntegerChoices):
        COMMON = 1, "Common"
        UNCOMMON = 2, "Uncommon"
        RARE = 3, "Rare"
        EPIC = 4, "Epic"
        LEGENDARY = 5, "Legendary"

    blueprint = models.ForeignKey(ItemBlueprint, on_delete=models.CASCADE)
    inventory = models.ForeignKey(
        Inventory,
        blank=True,
        null=True,
        on_delete=models.CASCADE
    )

    level = models.PositiveSmallIntegerField(default=1)
    amount = models.PositiveSmallIntegerField(default=1)
    rarity = models.PositiveSmallIntegerField(choices=Rarity.choices)

    min_damage = models.PositiveSmallIntegerField(default=0)
    max_damage = models.PositiveSmallIntegerField(default=0)
    defense = models.PositiveSmallIntegerField(default=0)
    health = models.PositiveSmallIntegerField(default=0)
    cost = models.PositiveSmallIntegerField(default=1)

    skin = models.ImageField(upload_to='skins/item', blank=True)

    def __str__(self):
        prefix = ""
        if self.blueprint.is_stackable:
            prefix = f"{self.amount} "

        return f"{prefix}{self.blueprint.name} (character: {self.inventory.character})"


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
