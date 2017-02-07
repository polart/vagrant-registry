from django.contrib import admin
from rest_framework.authtoken.admin import TokenAdmin


from rest_framework.authtoken.models import Token

from apps.users.models import MyToken


class MyTokenAdmin(TokenAdmin):
    list_display = ('key', 'user', 'created', 'expires', 'is_valid_nice')
    fields = ('user',)
    ordering = ('-created',)

    def is_valid_nice(self, obj):
        """Overrides `is_valid` property, so it can be shown as nice icon"""
        return obj.is_valid
    is_valid_nice.boolean = True
    is_valid_nice.short_description = 'Is valid'

admin.site.unregister(Token)
admin.site.register(MyToken, MyTokenAdmin)
