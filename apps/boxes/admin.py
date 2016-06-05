from django.contrib import admin

from apps.boxes.models import Box, BoxVersion, BoxProvider

admin.site.register(Box)
admin.site.register(BoxVersion)
admin.site.register(BoxProvider)
