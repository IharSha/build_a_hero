from django.contrib import admin

from .models import Character, CharacterAttributes, UserVisit


class CharacterAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')


admin.site.register(Character, CharacterAdmin)
admin.site.register(CharacterAttributes)
admin.site.register(UserVisit)

