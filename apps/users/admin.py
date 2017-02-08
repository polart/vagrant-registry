from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User, Group
from rest_framework.authtoken.admin import TokenAdmin

from rest_framework.authtoken.models import Token

from apps.users.models import MyToken, UserProfile


class MyTokenAdmin(TokenAdmin):
    list_display = ('key', 'user', 'created', 'expires', 'is_valid_nice')
    fields = ('user',)
    ordering = ('-created',)

    def is_valid_nice(self, obj):
        """Overrides `is_valid` property, so it can be shown as nice icon"""
        return obj.is_valid
    is_valid_nice.boolean = True
    is_valid_nice.short_description = 'Is valid'


class UserProfileAdminInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    # verbose_name = 'Permission'
    # verbose_name_plural = 'Permissions'


class MyUserAdmin(UserAdmin):
    model = User

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', )}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    list_filter = ('is_staff', 'is_active', 'profile__boxes_permissions', )
    list_display = ('username', 'email', 'first_name', 'last_name',
                    'is_staff', 'boxes_permissions',)

    inlines = [
        UserProfileAdminInline,
    ]

    def boxes_permissions(self, obj):
        return obj.profile.get_boxes_permissions_display()
    boxes_permissions.admin_order_field = 'profile__boxes_permissions'


admin.site.unregister(Token)
admin.site.unregister(User)
admin.site.unregister(Group)

admin.site.register(MyToken, MyTokenAdmin)
admin.site.register(User, MyUserAdmin)
