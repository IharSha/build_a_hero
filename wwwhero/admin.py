from django.contrib import admin

from .models import *


class CharacterAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'created_at', 'updated_at')


class CharacterCooldownAdmin(admin.ModelAdmin):
    list_display = ('type', 'until', 'character')


class CharacterSelectionAdmin(admin.ModelAdmin):
    list_display = ('user', 'character')


admin.site.register(Character, CharacterAdmin)
admin.site.register(CharacterAttributes)
admin.site.register(CharacterCooldown, CharacterCooldownAdmin)
admin.site.register(CharacterSelection, CharacterSelectionAdmin)
admin.site.register(UserVisit)
