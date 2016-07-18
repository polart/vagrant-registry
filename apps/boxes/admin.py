from django.contrib import admin

from apps.boxes.models import Box, BoxVersion, BoxProvider, BoxUpload


admin.site.register(Box)
admin.site.register(BoxVersion)
admin.site.register(BoxProvider)
admin.site.register(BoxUpload)
