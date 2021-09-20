from django.contrib import admin

from .models import *


class CharacterAdmin(admin.ModelAdmin):
    list_display = ("user", "name", "created_at", "updated_at")


class CharacterCooldownAdmin(admin.ModelAdmin):
    list_display = ("type", "until", "character")


class CharacterSelectionAdmin(admin.ModelAdmin):
    list_display = ("user", "character")


class CharacterLocationAdmin(admin.ModelAdmin):
    list_display = ("character", "location")


class LocationAdmin(admin.ModelAdmin):
    list_display = ("name", "min_level", "type", "is_active")


admin.site.register(Character, CharacterAdmin)
admin.site.register(CharacterAttributes)
admin.site.register(CharacterCooldown, CharacterCooldownAdmin)
admin.site.register(CharacterSelection, CharacterSelectionAdmin)
admin.site.register(CharacterLocation, CharacterLocationAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(LocationType)
admin.site.register(ItemBlueprint)
admin.site.register(Item)
admin.site.register(Inventory)
admin.site.register(UserVisit)
