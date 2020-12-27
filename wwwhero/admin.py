from django.contrib import admin

from .models import Character, CharacterAttributes


admin.site.register(Character)
admin.site.register(CharacterAttributes)
