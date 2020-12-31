from django.contrib import admin

from .models import Character, CharacterAttributes, CharacterSelection, UserVisit


class CharacterAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')


class CharacterSelectionAdmin(admin.ModelAdmin):
    list_display = ('user', 'character')


admin.site.register(Character, CharacterAdmin)
admin.site.register(CharacterAttributes)
admin.site.register(CharacterSelection, CharacterSelectionAdmin)
admin.site.register(UserVisit)
