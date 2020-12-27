from django.contrib import admin

from .models import Character, CharacterAttributes, UserVisit


admin.site.register(Character)
admin.site.register(CharacterAttributes)
admin.site.register(UserVisit)
