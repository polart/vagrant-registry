from django.contrib import admin
from guardian.admin import GuardedModelAdmin

from apps.boxes.models import Box, BoxVersion, BoxProvider, BoxUpload


class BoxAdmin(GuardedModelAdmin):
    pass


admin.site.register(Box, BoxAdmin)
admin.site.register(BoxVersion)
admin.site.register(BoxProvider)
admin.site.register(BoxUpload)
